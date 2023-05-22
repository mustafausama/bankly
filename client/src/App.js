import { BrowserRouter, Route, Routes } from "react-router-dom";
import Register from "./pages/Register/Register";
import Login from "./pages/Login/Login";
import Logout from "./pages/logout/Logout";
import RequiresAuth from "./components/RequiresAuth";
import Account from "./pages/Account/Account";
import AccountManagement from "./pages/Account/AccountManagement";
import { Container } from "react-bootstrap";
import Header from "./components/Header";
import { useEffect, useState } from "react";
import { auth } from "./utils/auth";
import Home from "./pages/Home";

function App() {
  const [access, setAccess] = useState();
  useEffect(() => {
    setAccess(auth());
  }, []);
  return (
    <BrowserRouter>
      <Header access={access} />
      <Container>
        <div className="mt-4">
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login setAccess={setAccess} />} />
            <Route path="/logout" element={<Logout setAccess={setAccess} />} />
            <Route
              path="/account"
              element={
                <RequiresAuth>
                  <Account />
                </RequiresAuth>
              }
            />
            <Route
              path="/account/:account_id"
              element={
                <RequiresAuth>
                  <AccountManagement />
                </RequiresAuth>
              }
            />
            <Route path="*" element={<Home access={access} />}></Route>
          </Routes>
        </div>
      </Container>
    </BrowserRouter>
  );
}

export default App;
