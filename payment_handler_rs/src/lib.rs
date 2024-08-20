use pyo3::prelude::*;
use std::collections::HashMap;
use std::f64;

#[pyclass]
pub struct PaymentHandler {
    payments: HashMap<String, Vec<f64>>,
    payment_counts: HashMap<String, usize>,
    current_balances: HashMap<String, f64>,
    cumulative_balances: HashMap<String, Vec<f64>>,
    var_cumulative_balances: HashMap<String, Vec<f64>>,
    periodic_average_payments: HashMap<String, Vec<f64>>,
    periodic_std_payments: HashMap<String, Vec<f64>>,
}

#[pymethods]
impl PaymentHandler {
    #[new]
    fn new() -> Self {
        PaymentHandler {
            payments: HashMap::new(),
            payment_counts: HashMap::new(),
            current_balances: HashMap::new(),
            cumulative_balances: HashMap::new(),
            var_cumulative_balances: HashMap::new(),
            periodic_average_payments: HashMap::new(),
            periodic_std_payments: HashMap::new(),
        }
    }

    fn initialize_merchant(&mut self, merchant_id: String) {
        if !self.payments.contains_key(&merchant_id) {
            self.payments.insert(merchant_id.clone(), Vec::new());
            self.payment_counts.insert(merchant_id.clone(), 0);
            self.current_balances.insert(merchant_id.clone(), 0.0);
            self.cumulative_balances.insert(merchant_id.clone(), vec![0.0]);
            self.var_cumulative_balances.insert(merchant_id.clone(), Vec::new());
        }
    }

    fn process_payment(&mut self, merchant_id: String, amount: f64) {
        self.initialize_merchant(merchant_id.clone());
        self.payments.get_mut(&merchant_id).unwrap().push(amount);
        let count = self.payment_counts.get_mut(&merchant_id).unwrap();
        *count += 1;
        let balance = self.current_balances.get_mut(&merchant_id).unwrap();
        *balance += amount;
        self.cumulative_balances.get_mut(&merchant_id).unwrap().push(*balance);
    }

    fn get_payment_count(&self, merchant_id: String) -> usize {
        self.payment_counts.get(&merchant_id).cloned().unwrap_or(0)
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

    fn update_periodic_statistics(&mut self, merchant_id: String, window_size: usize) -> PyResult<()> {
        if let Some(payments) = self.payments.get(&merchant_id) {
            if payments.len() >= window_size {
                let avg = self.calculate_periodic_average(payments.clone(), window_size)?;
                let std = self.calculate_periodic_std(payments.clone(), window_size)?;
                self.periodic_average_payments.entry(merchant_id.clone()).or_default().push(avg);
                self.periodic_std_payments.entry(merchant_id.clone()).or_default().push(std);
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

    fn calculate_balance_var(&mut self, merchant_id: String, confidence_level: f64) -> PyResult<f64> {
        if let Some(cumulative_balances) = self.cumulative_balances.get(&merchant_id) {
            if cumulative_balances.len() <= 1 {
                return Err(pyo3::exceptions::PyValueError::new_err("Not enough balance data to calculate VaR"));
            }
            let var = self.calculate_var(cumulative_balances.clone(), confidence_level)?;
            self.var_cumulative_balances.entry(merchant_id).or_default().push(var);
            Ok(var)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("Merchant ID not found"))
        }
    }
}

#[pymodule]
fn payment_handler_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PaymentHandler>()?;
    Ok(())
}
