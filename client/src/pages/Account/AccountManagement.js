import { useEffect, useState } from "react";
import { Alert, Button, Form, ListGroup } from "react-bootstrap";
import { useForm } from "react-hook-form";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import { auth } from "../../utils/auth";

const AccountManagement = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch,
    clearErrors,
    getValues,
    reset
  } = useForm();
  const params = useParams();
  const { account_id } = params;
  const [serverErrors, setServerErrors] = useState({});
  const [observe, setObserve] = useState(true);
  const [access, setAccess] = useState();
  const [account, setAccount] = useState({});
  const [statements, setStatements] = useState([]);
  useEffect(() => {
    setAccess(auth());
  }, [setAccess]);
  useEffect(() => {
    const subscription = watch(() => clearErrors("detail"));
    return () => subscription.unsubscribe();
  }, [watch, clearErrors]);
  useEffect(() => {
    const fetchStatements = async () => {
      const response = await fetch(
        `http://127.0.0.1:8000/api/accounts/${account_id}/statements/`,
        {
          headers: {
            Authorization: "Bearer " + access
          }
        }
      );
      const json = await response.json();
      return json;
    };
    const fetchAccount = async () => {
      const response = await fetch("http://127.0.0.1:8000/api/accounts/", {
        headers: {
          Authorization: "Bearer " + access
        }
      });
      const json = await response.json();
      return json.filter((account) => account.id === parseInt(account_id))[0];
    };

    if (access && account_id && observe) {
      fetchStatements().then((statements) => setStatements(statements));
      fetchAccount().then((account) => setAccount(account));
      setObserve(false);
    }
  }, [access, account_id, observe, setObserve]);

  const onSubmit = async (data) => {
    console.log(data, access);
    const response = await fetch(
      "http://127.0.0.1:8000/api/accounts/transactions/create/",
      {
        method: "POST",
        headers: {
          Authorization: "Bearer " + access,
          "Content-Type": "application/json"
        },

        body: JSON.stringify({ ...data, sender: account_id })
      }
    );
    const json = await response.json();

    if (response.ok) {
      toast.success("Transaction successful");
      reset();
      setObserve(true);
    } else {
      for (const [key, value] of Object.entries(json)) {
        setServerErrors({});
        if (key === "detail") setError(key, { type: "server", message: value });
        else
          setError(key, {
            type: "server",
            message: value[0].includes("object does not exist")
              ? "Account does not exist"
              : value[0]
          });
      }
    }
  };

  return (
    <>
      <h3 className="text-center">Account Details</h3>
      <h5>
        <strong>Account Number</strong>{" "}
        <span className="text-secondary">{account_id}</span>
      </h5>
      <h5>
        <strong>Balance</strong>{" "}
        <span className="text-secondary">{account.balance} EGP</span>
      </h5>
      <h3 className="text-center">Make a Transaction</h3>
      <Form onSubmit={handleSubmit(onSubmit)}>
        {errors.detail && (
          <Alert variant="danger">{errors.detail.message}</Alert>
        )}
        <Form.Group controlId="formBasicTransactionType">
          <Form.Label>Transaction Type</Form.Label>
          <Form.Select
            type="select"
            name="transaction_type"
            isInvalid={errors.transaction_type}
            {...register("transaction_type", { required: true })}
          >
            <option value="withdraw">Withdraw (no recipient)</option>
            <option value="pay_bill">Pay Bill (to a company account)</option>
            <option value="transfer">Transfer</option>
          </Form.Select>
          <Form.Control.Feedback type="invalid">
            {errors.transaction_type?.message || serverErrors.transaction_type}
          </Form.Control.Feedback>
        </Form.Group>
        {getValues("transaction_type") !== "withdraw" && (
          <Form.Group controlId="formBasicRecipient">
            <Form.Label>Recipient Account ID</Form.Label>
            <Form.Control
              type="number"
              name="recipient"
              isInvalid={errors.recipient}
              {...register("recipient", { required: true })}
            />
            <Form.Control.Feedback type="invalid">
              {errors.recipient?.message || serverErrors.recipient}
            </Form.Control.Feedback>
          </Form.Group>
        )}
        <Form.Group controlId="formBasicAmount">
          <Form.Label>Amount (EGP)</Form.Label>
          <Form.Control
            type="number"
            name="amount"
            step=".01"
            isInvalid={errors.amount}
            {...register("amount", { required: true, min: 1 })}
          />
          <Form.Control.Feedback type="invalid">
            {errors.amount?.message || serverErrors.amount}
          </Form.Control.Feedback>
          <Form.Text className="text-muted">Minimum amount is 1 EGP</Form.Text>
        </Form.Group>
        <Button variant="primary" type="submit">
          Submit
        </Button>
      </Form>
      <h3 className="text-center">Bank Statements</h3>
      {statements.length > 0 && (
        <ListGroup>
          {statements.map((statement) => (
            <ListGroup.Item className="d-flex flex-column align-content-between align-items-start">
              <span>
                <strong>Transaction Reference</strong>{" "}
                <span className="text-secondary">{statement.id}</span>
              </span>
              <span>
                <strong>Transaction Type</strong>{" "}
                <span className="text-secondary">
                  {statement.transaction_type === "transfer"
                    ? "Transfer"
                    : statement.transaction_type === "pay_bill"
                    ? "Pay Bill"
                    : "Withdraw"}
                </span>
              </span>
              <span>
                <strong>Recipient Account Number</strong>{" "}
                <span className="text-secondary">{statement.recipient}</span>
              </span>
              <span>
                <strong>Amount</strong>{" "}
                <span className="text-secondary">{statement.amount} EGP</span>
              </span>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </>
  );
};

export default AccountManagement;
