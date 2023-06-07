import { useEffect, useState } from "react";
import { Badge, Container, Nav, NavDropdown, Navbar } from "react-bootstrap";
import { NavLink } from "react-router-dom";
const Header = ({ access }) => {
  const [notifications, setNotifications] = useState([]);
  useEffect(() => {
    if (access) {
      const fetchNotifications = async () => {
        const response = await fetch(
          process.env.REACT_APP_SERVER + "/api/accounts/notifications/unread/",
          {
            headers: {
              Authorization: "Bearer " + access
            }
          }
        );
        const json = await response.json();
        return json;
      };
      fetchNotifications().then((res) => setNotifications(res));
    }
  }, [access]);
  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="#">Bankly</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link to={"/"} as={NavLink}>
              Home
            </Nav.Link>
            <Nav.Link to={"/account"} as={NavLink}>
              Dashboard
            </Nav.Link>
          </Nav>
          <Nav className="ms-auto">
            {!access ? (
              <>
                <Nav.Link to={"/login"} as={NavLink}>
                  Login
                </Nav.Link>
                <Nav.Link to={"/register"} as={NavLink}>
                  Register
                </Nav.Link>
              </>
            ) : (
              <>
                {notifications && (
                  <NavDropdown
                    title={
                      <span>
                        Notifications{" "}
                        <Badge bg="secondary">
                          {notifications
                            ? notifications.filter((not) => !not.is_read).length
                            : 0}
                        </Badge>
                      </span>
                    }
                    id="basic-nav-dropdown"
                    align="end"
                  >
                    {notifications
                      .filter((not) => !not.is_read)
                      .map((not) => (
                        <NavDropdown.Item onClick={console.log("")}>
                          {not.message}
                        </NavDropdown.Item>
                      ))}
                    {/* <NavDropdown.Divider />
                    {notifications
                      .filter((not) => not.is_read)
                      .map((not) => (
                        <NavDropdown.Item>{not.message}</NavDropdown.Item>
                      ))} */}
                  </NavDropdown>
                )}

                <Nav.Link to={"/logout"} as={NavLink}>
                  Logout
                </Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
