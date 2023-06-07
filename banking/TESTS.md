# TESTS

This app of the project uses Test-Driven Development (TDD) approach. Each functionality is first covered by tests, and then the implementation is done to make the tests pass. This ensures that all code is covered by tests and works as expected.

## Test Classes

### TestAccountCreation

This class tests the account creation functionality.

- `test_create_individual_account`: Tests the creation of an individual account and expects a successful response with the account type as 'individual'.
- `test_create_company_account`: Tests the creation of a company account and expects a successful response with the account type as 'company'.
- `test_create_default_account`: Tests the creation of a default account (without specifying the account type) and expects a successful response with the account type as 'individual'.
- `test_create_invalid_account`: Tests the creation of an account with an invalid account type and expects a bad request response.

### TestAccountRetrieval

This class tests the account retrieval functionality.

- `test_user_with_no_accounts`: Tests the retrieval of accounts for a user with no accounts and expects an empty list.
- `test_user_with_one_account`: Tests the retrieval of accounts for a user with one account and expects a list with one account.
- `test_user_with_two_accounts`: Tests the retrieval of accounts for a user with two accounts and expects a list with two accounts.

### TestTransactionConstraintsAPI

This class tests the transaction constraints at the API level.

- `test_withdraw_transaction_with_recipient`: Tests the withdrawal transaction with a recipient and expects a bad request response stating that the recipient must be empty for withdrawal transactions.
- `test_pay_bill_transaction_with_incorrect_recipient_type`: Tests the pay bill transaction with an incorrect recipient type and expects a bad request response stating that the recipient must be a company account for pay bill transactions.
- `test_transfer_transaction_without_recipient`: Tests the transfer transaction without a recipient and expects a bad request response stating that the recipient must be specified for transfer transactions.
- `test_transaction_with_insufficient_balance`: Tests the transaction with insufficient balance and expects a bad request response stating that the sender must have sufficient balance to perform the transaction.
- `test_transaction_with_unauthorized_sender`: Tests the transaction with an unauthorized sender and expects a forbidden response stating that the sender account does not belong to the authenticated user.
- `test_self_transactions`: Tests the self transactions and expects a bad request response stating that self transactions are not allowed.
- `test_successful_transfer_transaction` **[Integration Test]**: Tests a successful transfer transaction and expects a successful response. It also checks if the sender's and recipient's account balances are updated correctly.

### TestTransactionConstraintsModel

This class tests the transaction constraints at the model level. The methods in this class are similar to those in `TestTransactionConstraintsAPI`, but they test the constraints at the model level.

### TransactionsIntegrationTest **[Integration Test]**

This class tests the transactions integration.

- `test_get_notificatios`: Tests the retrieval of notifications for two users and expects a successful response with correct notification messages.
- `test_get_bank_statements`: Tests the retrieval of bank statements for an account and expects a successful response with correct transaction details.

### NotificationTestCase

This class tests the notification functionality.

- `test_notification_creation`: Tests the creation of a notification and expects a successful creation with correct user and message.
- `test_notification_mark_as_read`: Tests marking a notification as read and expects the notification to be marked as read.
- `test_notification_str_representation`: Tests the string representation of a notification and expects it to be equal to the notification message.

### TransactionTestCase

This class tests the transaction functionality.

- `test_pay_bill`: Tests the pay bill transaction and expects a successful transaction with correct sender, recipient, transaction type, and amount. It also checks if the sender's and recipient

's account balances are updated correctly.
- `test_withdraw_transaction`: Tests the withdrawal transaction and expects a successful transaction with correct sender, transaction type, and amount. It also checks if the sender's account balance is updated correctly.

## Integration Testing

In the integration testing, more possible scenarios of stubs and drivers can be:

- Stubs: In this context, stubs can be used to simulate the behavior of external dependencies such as a payment gateway or a third-party API. For example, when testing the transaction functionality, a stub can be used to simulate the response of a payment gateway.

- Drivers: Drivers can be used to trigger the functionality that needs to be tested. For example, in the `TransactionsIntegrationTest` class, the `test_get_notificatios` and `test_get_bank_statements` methods act as drivers that trigger the retrieval of notifications and bank statements, respectively.

The integration tests ensure that the different units of the application work together as expected. They test the application as a whole, as opposed to unit tests which test individual components in isolation.