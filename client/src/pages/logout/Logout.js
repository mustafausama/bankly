import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Logout = ({ setAccess }) => {
  const navigate = useNavigate();
  useEffect(() => {
    localStorage.removeItem("auth");
    setAccess(null);
    navigate("/");
  }, [navigate, setAccess]);
  return <></>;
};

export default Logout;
