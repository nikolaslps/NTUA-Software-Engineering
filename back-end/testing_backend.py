import unittest
import requests
import mysql.connector

# Configuration for the database and API
DB_CONFIG = {
    'user': 'root',
    'password': 'volara',
    'host': 'localhost',
    'database': 'toll_system'
}

API_BASE_URL = 'http://localhost:9115'

class TestBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Connect to the database
        cls.db_connection = mysql.connector.connect(**DB_CONFIG)
        cls.cursor = cls.db_connection.cursor()

    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.cursor.close()
        cls.db_connection.close()

    def test_healthcheck(self):
        response = requests.get(f'{API_BASE_URL}/admin/healthcheck')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('n_stations', data)
        self.assertIn('n_tags', data)
        self.assertIn('n_passes', data)

    def test_reset_stations(self):
        response = requests.post(f'{API_BASE_URL}/admin/resetstations')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'OK')

    def test_reset_passes(self):
        response = requests.post(f'{API_BASE_URL}/admin/resetpasses')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'OK')

    def test_add_passes(self):
        # Assuming you have a sample CSV file for testing
        with open('passes-sample.csv', 'rb') as f:
            response = requests.post(f'{API_BASE_URL}/admin/addpasses', files={'file': f})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'OK')

    def test_toll_station_passes(self):
        response = requests.get(f'{API_BASE_URL}/tollStationPasses/AM01/20230101/20231231')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('passList', data)

    def test_pass_analysis(self):
        response = requests.get(f'{API_BASE_URL}/passAnalysis/AM/NO/20230101/20231231')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('passList', data)

    def test_passes_cost(self):
        response = requests.get(f'{API_BASE_URL}/passesCost/AM/NO/20230101/20231231')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('nPasses', data)
        self.assertIn('passesCost', data)

    def test_charges_by(self):
        response = requests.get(f'{API_BASE_URL}/chargesBy/AM/20230101/20231231')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('vOpList', data)

    def test_show_debts(self):
        response = requests.get(f'{API_BASE_URL}/ShowDebts/NO')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('DebtsList', data)

    def test_show_profits(self):
        response = requests.get(f'{API_BASE_URL}/ShowProfits/NO')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('DebtsList', data)

    def test_show_statistics(self):
        response = requests.get(f'{API_BASE_URL}/ShowStatistics/NO')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('DebtsList', data)

if __name__ == '__main__':
    unittest.main()