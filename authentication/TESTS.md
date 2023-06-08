# TESTS

This app of the project uses Test-Driven Development (TDD) approach. Each functionality is first covered by tests, and then the implementation is done to make the tests pass. This ensures that all code is covered by tests and works as expected.

## Test Classes

### TestUserAuthentication

This class tests the user authentication functionality.

- `test_successful_login`: Tests the login functionality with correct credentials and expects a successful response with an access token.
- `test_unsuccessful_login`: Tests the login functionality with incorrect credentials and expects an unauthorized response.

### TestUserRegistration

This class tests the user registration functionality.

- `test_successful_registration`: Tests the registration functionality with a new username and a valid password and expects a successful response with the username.
- `test_registration_missing_field`: Tests the registration functionality without a username and expects a bad request response.
- `test_registration_username_taken`: Tests the registration functionality with a taken username and expects a bad request response.

### UserRegistrationLoginIntegrationTest **[Integration Test]**

This class tests the integration of user registration and login.

- `test_user_registration_and_login`: Tests the user registration and then login with the registered credentials. It expects a successful response from both registration and login, with the username from the registration response and an access token from the login response.

## Integration Testing

In the integration testing, possible scenarios of stubs and drivers can be:

- Stubs: Stubs were used instead of, for instance, the login logic in the `test_user_registration_and_login` unit test, to return a random access token of a consistent and an inconsistent value to test the app.

- Drivers: Drivers were used to trigger the functionality that needs to be tested. For example, in the `UserRegistrationLoginIntegrationTest` class, the `test_user_registration_and_login` method acts as a driver that triggers the registration and login functionalities. Drivers were also used in the app where the API provider view `TokenObtainPairView` was not yet ready to call the correct serializer class `TokenObtainPairSerializer`, so a driver was created to mimic the API view and call the serializer class.


The integration tests ensure that the different units of the application work together as expected. They test the application as a whole, as opposed to unit tests which test individual components in isolation.