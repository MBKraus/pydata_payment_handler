use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

#[pyclass]
struct PaymentHandler {
    transactions: HashMap<String, Vec<f64>>,
    moving_averages: HashMap<String, Vec<f64>>,
}

#[pymethods]
impl PaymentHandler {
    #[new]
    fn new() -> Self {
        PaymentHandler {
            transactions: HashMap::new(),
            moving_averages: HashMap::new(),
        }
    }

    fn add_transaction(&mut self, merchant_id: String, amount: f64) {
        self.transactions
            .entry(merchant_id.clone())
            .or_insert_with(Vec::new)
            .push(amount);
    }

    fn calculate_moving_average(&mut self, merchant_id: String, window_size: usize) -> PyResult<()> {
        if let Some(transactions) = self.transactions.get(&merchant_id) {
            if transactions.len() >= window_size {
                let sum: f64 = transactions[transactions.len() - window_size..].iter().sum();
                let moving_average = sum / window_size as f64;
                self.moving_averages
                    .entry(merchant_id)
                    .or_insert_with(Vec::new)
                    .push(moving_average);
            }
        }
        Ok(())
    }

    fn summarize(&self, merchant_id: String) -> PyResult<Py<PyDict>> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let summary = PyDict::new(py);

        if let Some(transactions) = self.transactions.get(&merchant_id) {
            let total: f64 = transactions.iter().sum();
            let average: f64 = total / transactions.len() as f64;
            let highest: f64 = *transactions.iter().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
            let lowest: f64 = *transactions.iter().min_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();

            summary.set_item("total", total)?;
            summary.set_item("average", average)?;
            summary.set_item("highest", highest)?;
            summary.set_item("lowest", lowest)?;
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found"));
        }

        Ok(summary.into())
    }
}

#[pymodule]
fn payment_handler_rs(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PaymentHandler>()?;
    Ok(())
}
