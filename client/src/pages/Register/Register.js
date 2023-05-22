import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Button, Container, Form } from "react-bootstrap";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

function Register() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch,
    clearErrors
  } = useForm();
  const [serverErrors, setServerErrors] = useState({});
  const navigate = useNavigate();
  useEffect(() => {
    const subscription = watch(() => clearErrors("detail"));
    return () => subscription.unsubscribe();
  }, [watch, clearErrors]);

  const onSubmit = async (data) => {
    const response = await fetch(
      "http://127.0.0.1:8000/api/authentication/register/",
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
      toast.success("Registered Successfully");
      navigate("/login", { state: { username: data.username } });
    } else {
      setServerErrors({});
      for (const [key, value] of Object.entries(json)) {
        if (key === "detail") setError(key, { type: "server", message: value });
        else setError(key, { type: "server", message: value[0] });
      }
    }
  };

  return (
    <Container>
      <Form onSubmit={handleSubmit(onSubmit)}>
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
        <Form.Group controlId="formBasicEmail">
          <Form.Label>Email address</Form.Label>
          <Form.Control
            type="email"
            placeholder="Enter email"
            isInvalid={errors.email}
            {...register("email", { required: false })}
          />
          <Form.Control.Feedback type="invalid">
            {errors.email?.message || serverErrors.email}
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

export default Register;
