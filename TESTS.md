# TESTS

This project uses Test-Driven Development (TDD) approach. Each functionality is first covered by tests, and then the implementation is done to make the tests pass. This ensures that all code is covered by tests and works as expected.

You can find detailed descriptions of the other unit tests in the following README files:

- [Banking Tests README](banking/TESTS.md)
- [Authentication Tests README](authentication/TESTS.md)

## Test Classes

### BigBangIntegrationTest

This class tests the integration of multiple functionalities in a single test, often referred to as a "Big Bang" integration test.

- `test_big_bang`: This method tests the following functionalities in sequence:
  - User Registration: It tests the registration of a new user and expects a successful response with the username.
  - User Login: It tests the login of the registered user and expects a successful response with an access and refresh token.
  - User Refresh Login: It tests the refresh login functionality using the refresh token and expects a successful response with a new access token.
  - Create Account: It tests the creation of an account and expects a successful response with the account type.
  - Hard-update balance: It updates the balance of the created account to 1000 using the ORM and expects the updated balance to be 1000.
  - Create Transaction: It tests the creation of a withdrawal transaction and expects a successful response.
  - Check Account list: It tests the retrieval of the account list and expects a list with one account with a balance of 500.
  - Check Bank Statement: It tests the retrieval of the bank statement and expects a statement with one transaction of type 'withdrawal' and amount 500.
  - Check Unread Notifications: It tests the retrieval of unread notifications and expects one notification with a message about the transaction.

## Integration Testing

In the integration testing, possible scenarios of stubs and drivers can be:

- Stubs: In this context, stubs can be used to simulate the behavior of external dependencies such as a payment gateway or a third-party API. For example, when testing the transaction functionality, a stub can be used to simulate the response of a payment gateway.

- Drivers: Drivers can be used to trigger the functionality that needs to be tested. For example, in the `BigBangIntegrationTest` class, the `test_big_bang` method acts as a driver that triggers multiple functionalities in sequence.

The integration tests ensure that the different units of the application work together as expected. They test the application as a whole, as opposed to unit tests which test individual components in isolation.