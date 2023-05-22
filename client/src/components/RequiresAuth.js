import { useEffect, useState } from "react";
import { auth } from "../utils/auth";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
const RequiresAuth = ({ children }) => {
  const navigate = useNavigate();
  const [permitted, setPermitted] = useState(false);
  useEffect(() => {
    if (!auth()) {
      toast.error("You need to be logged in");
      navigate("/login");
    } else setPermitted(true);
  }, [navigate]);
  return <>{permitted && children}</>;
};

export default RequiresAuth;
