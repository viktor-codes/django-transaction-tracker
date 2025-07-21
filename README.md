# Django Transaction Tracker

-----


## 🏁 Getting Started

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/viktor-codes/django-transaction-tracker.git
    cd django-transaction-tracker
    ```

2.  **Build and run the Docker containers:**

    ```bash
    docker-compose up --build -d
    ```

    This command will build the `web` service image, pull the `postgres` image, and start both containers in detached mode.

3.  **Run database migrations:**
    Once the containers are up, execute database migrations to set up the necessary tables:

    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **Create a superuser (optional, but recommended for admin access):**

    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

    Follow the prompts to create your admin username and password.

### Accessing the Application

After completing the installation steps, the application should be accessible in your web browser.

  * **Web Application:** Open your browser and navigate to `http://localhost:8001`
  * **Django Admin:** Access the Django administration panel at `http://localhost:8001/admin` using the superuser credentials you created.

## 🧪 Running Tests

To ensure the core logic and functionalities are working correctly, you can run the automated tests.

Execute the following command from the project root directory (where `docker-compose.yml` is located):

```bash
docker-compose exec web python manage.py test
```

## 🔌 API Integration Details

The application can import transactions from an external, read-only API.

  * **API Endpoint:**
    `GET https://685efce5c55df675589d49df.mockapi.io/api/v1/transactions`

  * **API Field Mapping to Transaction Model:**
    The external API's response fields are mapped to the local `Transaction` model as follows:

      * `id` (string) → `transaction_code` (unique identifier for API-imported transactions)
      * `createdAt` (string, e.g., "2025-06-27T12:52:58.669Z") → `creation_date` (datetime field in the model)
      * `amount` (positive float) → `amount` (decimal field in the model)
      * `type` (string, either "deposit" or "expense") → `type` (string/choice field in the model)

  * **Notes on Amount Handling:**

      * The `amount` field in the database always stores a **positive value**, consistent with the API.
      * When calculating the `running_balance`, the application dynamically adjusts the amount based on the `type`:
          * For `deposit` types, the `amount` is added to the balance.
          * For `expense` types, the `amount` is subtracted from the balance.
      * On the UI, expenses are displayed with a negative sign (e.g., `-X.XX`) and often styled differently (e.g., red color).

  * **Notes on Transaction Codes for New Transactions:**

      * Transactions imported from the API use the `id` from the API response as their `transaction_code` to maintain uniqueness and traceability.
      * For transactions added **manually** by the user (not from the API), a unique transaction code is generated locally (e.g., `TXN-0001`, `TXN-0002`, etc.) to distinguish them from API-imported ones and ensure uniqueness in the database.

## 💡 Usage

Once the application is running, you can:

  * **View Transactions:** See a paginated list of all your transactions with a running balance.
  * **Add New Transactions:** Use the dedicated form/modal to record new income or expenses. These are saved to your local database only.
  * **Edit/Delete Transactions:** Modify or remove existing transactions from your history.
  * **Import Transactions:** Click the "Load Transactions" button to fetch and store data from the external API.

## 📋 Assumptions & Dependencies

  * **Single User System:** The application is designed for a single user; no user authentication or multi-user features are implemented.
  * **Read-Only API:** The external API is treated as read-only; no attempts are made to send data back to it.
  * **API Data Integrity:** Assumes the external API provides `amount` as a positive float and `type` as either "deposit" or "expense". Basic error handling for API call failures is in place.
  * **Database Uniqueness:** Assumes that the `id` from the API for imported transactions, and the generated codes for local transactions, are sufficient to maintain uniqueness in the database.
  * **Frontend Framework:** Relies on Bootstrap 5 for UI components and HTMX for dynamic interactions.

-----