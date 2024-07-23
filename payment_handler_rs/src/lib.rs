use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::f64;
use std::error::Error;
use std::cmp;

#[pyclass]
struct PaymentHandler {
    transactions: HashMap<String, Vec<f64>>,
    transaction_counts: HashMap<String, usize>,
    periodic_averages: HashMap<String, Vec<f64>>,
    periodic_stddevs: HashMap<String, Vec<f64>>,
}

#[pymethods]
impl PaymentHandler {
    #[new]
    fn new() -> Self {
        PaymentHandler {
            transactions: HashMap::new(),
            transaction_counts: HashMap::new(),
            periodic_averages: HashMap::new(),
            periodic_stddevs: HashMap::new(),
        }
    }

    fn add_transaction(&mut self, merchant_id: String, amount: f64) {
        self.transactions
            .entry(merchant_id.clone())
            .or_insert_with(Vec::new)
            .push(amount);

        let count = self.transaction_counts.entry(merchant_id.clone()).or_insert(0);
        *count += 1;
    }

    fn get_transaction_count(&self, merchant_id: String) -> PyResult<usize> {
        match self.transaction_counts.get(&merchant_id) {
            Some(&count) => Ok(count),
            None => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found")),
        }
    }

    fn compute_totals(&self, merchant_id: String) -> PyResult<f64> {
        match self.transactions.get(&merchant_id) {
            Some(transactions) => Ok(transactions.iter().sum()),
            None => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found")),
        }
    }

    fn compute_average(&self, merchant_id: String) -> PyResult<f64> {
        match self.transactions.get(&merchant_id) {
            Some(transactions) => {
                let total: f64 = transactions.iter().sum();
                Ok(total / transactions.len() as f64)
            }
            None => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found")),
        }
    }

    fn find_extremes(&self, merchant_id: String) -> PyResult<(f64, f64)> {
        match self.transactions.get(&merchant_id) {
            Some(transactions) => {
                let highest = transactions.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
                let lowest = transactions.iter().cloned().fold(f64::INFINITY, f64::min);
                Ok((highest, lowest))
            }
            None => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found")),
        }
    }

    fn summarize(&self, merchant_id: String) -> PyResult<Py<PyDict>> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let summary = PyDict::new(py);

        if let Some(transactions) = self.transactions.get(&merchant_id) {
            let total = self.compute_totals(merchant_id.clone())?;
            let average = self.compute_average(merchant_id.clone())?;
            let (highest, lowest) = self.find_extremes(merchant_id)?;

            summary.set_item("total", total)?;
            summary.set_item("average", average)?;
            summary.set_item("highest", highest)?;
            summary.set_item("lowest", lowest)?;
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found"));
        }

        Ok(summary.into())
    }

    fn calculate_periodic_average(&self, transactions: Vec<f64>, window_size: usize) -> f64 {
        transactions[transactions.len() - window_size..].iter().sum::<f64>() / window_size as f64
    }

    fn calculate_periodic_stddev(&self, transactions: Vec<f64>, window_size: usize) -> f64 {
        let periodic_average = self.calculate_periodic_average(transactions.clone(), window_size);
        let variance = transactions[transactions.len() - window_size..]
            .iter()
            .map(|x| (x - periodic_average).powi(2))
            .sum::<f64>() / window_size as f64;
        variance.sqrt()
    }

    fn update_periodic_statistics(&mut self, merchant_id: String, window_size: usize) -> PyResult<()> {
        if let Some(transactions) = self.transactions.get(&merchant_id) {
            if transactions.len() >= window_size {
                let transactions_clone = transactions.clone();
                let periodic_average = self.calculate_periodic_average(transactions_clone.clone(), window_size);
                let periodic_stddev = self.calculate_periodic_stddev(transactions_clone, window_size);

                self.periodic_averages
                    .entry(merchant_id.clone())
                    .or_insert_with(Vec::new)
                    .push(periodic_average);
                self.periodic_stddevs
                    .entry(merchant_id)
                    .or_insert_with(Vec::new)
                    .push(periodic_stddev);
            }
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found"))
        }
    }
}

#[pymodule]
fn payment_handler_rs(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PaymentHandler>()?;
    Ok(())
}
