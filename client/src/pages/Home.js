import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Home = ({ access }) => {
  const navigate = useNavigate();
  useEffect(() => {
    if (!access) navigate("/login");
    else navigate("/account");
  }, [access, navigate]);
  return <></>;
};

export default Home;
