import { useEffect, useState } from "react";
import { Alert, Button, Form, ListGroup } from "react-bootstrap";
import { useForm } from "react-hook-form";
import { NavLink } from "react-router-dom";
import { toast } from "react-toastify";
import { auth } from "../../utils/auth";

const Account = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch,
    clearErrors,
    reset
  } = useForm();
  const [serverErrors, setServerErrors] = useState({});
  const [observe, setObserve] = useState(true);
  const [access, setAccess] = useState("");
  const [accounts, setAccounts] = useState([]);
  useEffect(() => {
    setAccess(auth());
  }, [setAccess]);
  useEffect(() => {
    const subscription = watch(() => clearErrors("detail"));
    return () => subscription.unsubscribe();
  }, [watch, clearErrors]);
  useEffect(() => {
    const fetchAccounts = async () => {
      const response = await fetch("http://127.0.0.1:8000/api/accounts/", {
        headers: {
          Authorization: "Bearer " + access
        }
      });
      const json = await response.json();
      return json;
    };
    if (access && observe) {
      fetchAccounts().then((accounts) => setAccounts(accounts));
      setObserve(false);
    }
  }, [access, observe, setObserve]);

  const onSubmit = async (data) => {
    console.log(data, access);
    const response = await fetch("http://127.0.0.1:8000/api/accounts/create/", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + access,
        "Content-Type": "application/json"
      },

      body: JSON.stringify(data)
    });
    const json = await response.json();

    if (response.ok) {
      toast.success("Account Created successfully");
      reset();
      setObserve(true);
    } else {
      for (const [key, value] of Object.entries(json)) {
        setServerErrors({});
        if (key === "detail") setError(key, { type: "server", message: value });
        else setError(key, { type: "server", message: value[0] });
      }
    }
  };

  return (
    <>
      <h3 className="text-center">Create a new bank account</h3>
      <Form onSubmit={handleSubmit(onSubmit)}>
        {errors.detail && (
          <Alert variant="danger">{errors.detail.message}</Alert>
        )}
        <Form.Group controlId="formBasicAccountType">
          <Form.Label>Account Type</Form.Label>
          <Form.Select
            type="select"
            name="account_type"
            isInvalid={errors.account_type}
            {...register("account_type", { required: true })}
          >
            <option value="select">Select Account Type</option>
            <option value="individual">Individual Account</option>
            <option value="company">Company Account</option>
          </Form.Select>
          <Form.Control.Feedback type="invalid">
            {errors.account_type?.message || serverErrors.account_type}
          </Form.Control.Feedback>
        </Form.Group>
        <Button variant="primary" type="submit">
          Submit
        </Button>
      </Form>
      <h3 className="text-center">All accounts</h3>
      {accounts.length > 0 && (
        <ListGroup>
          {accounts.map((account) => (
            <ListGroup.Item className="d-flex justify-content-between align-items-center">
              <span className="d-flex flex-column gap-3 align-items-start">
                <span>
                  <strong>Account Number</strong>{" "}
                  <span className="text-secondary">{account.id}</span>
                </span>
                <span>
                  <strong>Account Type</strong>{" "}
                  <span className="text-secondary">{account.account_type}</span>
                </span>
                <span>
                  <strong>Balance</strong>{" "}
                  <span className="text-secondary">{account.balance} EGP</span>
                </span>
              </span>
              <NavLink to={`/account/${account.id}`}>
                <Button>Manage</Button>
              </NavLink>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </>
  );
};

export default Account;
