import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Alert, Button, Container, Form } from "react-bootstrap";
import { toast } from "react-toastify";
import { useLocation, useNavigate } from "react-router-dom";
import { auth } from "../../utils/auth";

function Login({ setAccess }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    setValue,
    watch,
    clearErrors
  } = useForm();
  const [serverErrors, setServerErrors] = useState({});
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (auth()) {
      toast.info("You are already logged in");
      navigate("/account");
    }
  }, [navigate]);
  useEffect(() => {
    if (location.state) {
      for (let [key, value] of Object.entries(location.state)) {
        setValue(key, value);
      }
    }
  }, [location, setValue]);

  useEffect(() => {
    const subscription = watch(() => clearErrors("detail"));
    return () => subscription.unsubscribe();
  }, [watch, clearErrors]);
  const onSubmit = async (data) => {
    const response = await fetch(
      process.env.REACT_APP_SERVER + "/api/authentication/token/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify(data)
      }
    );
    const json = await response.json();

    if (response.ok) {
      toast.success("Logged in Successfully");
      localStorage.setItem("auth", JSON.stringify(json));
      setAccess(auth());
      navigate("/");
    } else {
      for (const [key, value] of Object.entries(json)) {
        setServerErrors({});
        if (key === "detail") setError(key, { type: "server", message: value });
        else setError(key, { type: "server", message: value[0] });
      }
    }
  };

  return (
    <Container>
      <Form onSubmit={handleSubmit(onSubmit)}>
        {errors.detail && (
          <Alert variant="danger">{errors.detail.message}</Alert>
        )}
        <Form.Group controlId="formBasicUsername">
          <Form.Label>Username</Form.Label>
          <Form.Control
            type="text"
            placeholder="Enter username"
            isInvalid={errors.username}
            {...register("username", { required: true })}
          />
          <Form.Control.Feedback type="invalid">
            {errors.username?.message || serverErrors.username}
          </Form.Control.Feedback>
        </Form.Group>
        <Form.Group controlId="formBasicPassword">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            placeholder="Password"
            isInvalid={errors.password}
            {...register("password", { required: true })}
          />
          <Form.Control.Feedback type="invalid">
            {errors.password?.message || serverErrors.password}
          </Form.Control.Feedback>
        </Form.Group>
        <Button variant="primary" type="submit">
          Submit
        </Button>
      </Form>
    </Container>
  );
}

export default Login;
