use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

#[pyclass]
struct PaymentHandler {
    transactions: HashMap<String, Vec<f64>>,
    transaction_counts: HashMap<String, usize>,
    periodic_averages: HashMap<String, Vec<f64>>,
    periodic_stddevs: HashMap<String, Vec<f64>>,
    periodic_statistics_interval: usize,
    periodic_statistics_window_size: usize,
}

#[pymethods]
impl PaymentHandler {
    #[new]
    fn new(periodic_statistics_interval: usize, periodic_statistics_window_size: usize) -> Self {
        PaymentHandler {
            transactions: HashMap::new(),
            transaction_counts: HashMap::new(),
            periodic_averages: HashMap::new(),
            periodic_stddevs: HashMap::new(),
            periodic_statistics_interval,
            periodic_statistics_window_size,
        }
    }

    fn add_transaction(&mut self, merchant_id: String, amount: f64) {
        self.transactions
            .entry(merchant_id.clone())
            .or_insert_with(Vec::new)
            .push(amount);

        let count = self.transaction_counts.entry(merchant_id.clone()).or_insert(0);
        *count += 1;

        // Check if the transaction count is even and update periodic statistics
        if *count % self.periodic_statistics_interval == 0 {
            self.update_periodic_statistics(&merchant_id, self.periodic_statistics_window_size)
                .expect("Failed to update periodic statistics");
        }
    }

    fn get_transaction_count(&self, merchant_id: &str) -> PyResult<usize> {
        match self.transaction_counts.get(merchant_id) {
            Some(&count) => Ok(count),
            None => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found")),
        }
    }

    fn update_periodic_statistics(&mut self, merchant_id: &str, window_size: usize) -> PyResult<()> {
        if let Some(transactions) = self.transactions.get(merchant_id) {
            if transactions.len() >= window_size {
                let transactions_clone = transactions.clone();
                let periodic_average = self.calculate_periodic_average(transactions_clone.clone(), window_size);
                let periodic_stddev = self.calculate_periodic_stddev(transactions_clone, window_size);

                self.periodic_averages
                    .entry(merchant_id.to_string())
                    .or_insert_with(Vec::new)
                    .push(periodic_average);
                self.periodic_stddevs
                    .entry(merchant_id.to_string())
                    .or_insert_with(Vec::new)
                    .push(periodic_stddev);
            }
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Merchant ID not found"))
        }
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
