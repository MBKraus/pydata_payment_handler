use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::HashMap;
use std::f64;
use std::sync::{Arc, Mutex};

#[pyclass]
pub struct PaymentHandlerParallel {
    payments: Arc<Mutex<HashMap<String, Vec<f64>>>>,
    payment_counts: Arc<Mutex<HashMap<String, usize>>>,
    current_balances: Arc<Mutex<HashMap<String, f64>>>,
    cumulative_balances: Arc<Mutex<HashMap<String, Vec<f64>>>>,
    var_cumulative_balances: Arc<Mutex<HashMap<String, Vec<f64>>>>,
    periodic_average_payments: Arc<Mutex<HashMap<String, Vec<f64>>>>,
    periodic_std_payments: Arc<Mutex<HashMap<String, Vec<f64>>>>,
}

#[pymethods]
impl PaymentHandlerParallel {
    #[new]
    fn new() -> Self {
        PaymentHandlerParallel {
            payments: Arc::new(Mutex::new(HashMap::new())),
            payment_counts: Arc::new(Mutex::new(HashMap::new())),
            current_balances: Arc::new(Mutex::new(HashMap::new())),
            cumulative_balances: Arc::new(Mutex::new(HashMap::new())),
            var_cumulative_balances: Arc::new(Mutex::new(HashMap::new())),
            periodic_average_payments: Arc::new(Mutex::new(HashMap::new())),
            periodic_std_payments: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    fn initialize_merchant(&self, merchant_id: &str) {
        let mut payments = self.payments.lock().unwrap();
        if !payments.contains_key(merchant_id) {
            payments.insert(merchant_id.to_string(), Vec::new());
            self.payment_counts.lock().unwrap().insert(merchant_id.to_string(), 0);
            self.current_balances.lock().unwrap().insert(merchant_id.to_string(), 0.0);
            self.cumulative_balances.lock().unwrap().insert(merchant_id.to_string(), vec![0.0]);
            self.var_cumulative_balances.lock().unwrap().insert(merchant_id.to_string(), Vec::new());
        }
    }

    fn process_payments(
        &self,
        payments: Vec<(String, f64)>,
        periodic_statistics_interval: usize,
        periodic_statistics_window_size: usize,
        confidence_interval: f64,
    ) {
        payments.into_par_iter().for_each(|(merchant_id, amount)| {
            self.initialize_merchant(&merchant_id);

            // Process payment
            let mut payments = self.payments.lock().unwrap();
            payments.get_mut(&merchant_id).unwrap().push(amount);

            let mut payment_counts = self.payment_counts.lock().unwrap();
            let count = payment_counts.get_mut(&merchant_id).unwrap();
            *count += 1;

            let mut current_balances = self.current_balances.lock().unwrap();
            let balance = current_balances.get_mut(&merchant_id).unwrap();
            *balance += amount;

            let mut cumulative_balances = self.cumulative_balances.lock().unwrap();
            cumulative_balances.get_mut(&merchant_id).unwrap().push(*balance);

            // Update statistics periodically
            if *count % periodic_statistics_interval == 0 {
                drop(payments); // Release lock before calling self methods
                drop(payment_counts);
                drop(current_balances);
                drop(cumulative_balances);

                // Correct method call
                self.calculate_periodic_statistics(merchant_id.clone(), periodic_statistics_window_size).unwrap();
                self.calculate_balance_var(merchant_id.clone(), confidence_interval).unwrap();
            }
        });
    }

    fn calculate_periodic_average(&self, values: Vec<f64>, window_size: usize) -> PyResult<f64> {
        if values.len() < window_size {
            return Err(pyo3::exceptions::PyValueError::new_err("Not enough values to calculate average"));
        }
        let sum: f64 = values.iter().rev().take(window_size).sum();
        Ok(sum / window_size as f64)
    }

    fn calculate_periodic_std(&self, values: Vec<f64>, window_size: usize) -> PyResult<f64> {
        let avg = self.calculate_periodic_average(values.clone(), window_size)?;
        let variance: f64 = values.iter().rev().take(window_size).map(|&x| (x - avg).powi(2)).sum();
        Ok((variance / window_size as f64).sqrt())
    }

    fn calculate_periodic_statistics(&self, merchant_id: String, window_size: usize) -> PyResult<()> {
        let payments = {
            let payments = self.payments.lock().unwrap();
            payments.get(&merchant_id).cloned()
        };

        if let Some(payments) = payments {
            if payments.len() >= window_size {
                let avg = self.calculate_periodic_average(payments.clone(), window_size)?;
                let std = self.calculate_periodic_std(payments.clone(), window_size)?;
                let mut periodic_average_payments = self.periodic_average_payments.lock().unwrap();
                periodic_average_payments.entry(merchant_id.clone()).or_default().push(avg);
                let mut periodic_std_payments = self.periodic_std_payments.lock().unwrap();
                periodic_std_payments.entry(merchant_id.clone()).or_default().push(std);
                Ok(())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err("Not enough values to update statistics"))
            }
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("Merchant ID not found"))
        }
    }

    fn calculate_var(&self, values: Vec<f64>, confidence_level: f64) -> PyResult<f64> {
        if values.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err("The values list is empty"));
        }
        let mut sorted_values = values.clone();
        sorted_values.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let index = ((1.0 - confidence_level) * sorted_values.len() as f64).floor() as usize;
        Ok(sorted_values[index])
    }

    fn calculate_balance_var(&self, merchant_id: String, confidence_level: f64) -> PyResult<f64> {
        let cumulative_balances = {
            let cumulative_balances = self.cumulative_balances.lock().unwrap();
            cumulative_balances.get(&merchant_id).cloned()
        };

        if let Some(cumulative_balances) = cumulative_balances {
            if cumulative_balances.len() <= 1 {
                return Err(pyo3::exceptions::PyValueError::new_err("Not enough balance data to calculate VaR"));
            }
            let var = self.calculate_var(cumulative_balances.clone(), confidence_level)?;
            let mut var_cumulative_balances = self.var_cumulative_balances.lock().unwrap();
            var_cumulative_balances.entry(merchant_id).or_default().push(var);
            Ok(var)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("Merchant ID not found"))
        }
    }
}

#[pymodule]
fn payment_handler_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PaymentHandlerParallel>()?;
    Ok(())
}
