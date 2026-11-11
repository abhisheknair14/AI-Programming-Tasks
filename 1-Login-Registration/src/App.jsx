import { useState, useEffect } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
  updateProfile
} from "firebase/auth";

import {
  doc,
  setDoc,
  getDoc,
  serverTimestamp
} from "firebase/firestore";

import { auth, db } from "./firebase";
import "./App.css";

function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        const userDoc = await getDoc(doc(db, "users", currentUser.uid));

        setUser({
          ...currentUser,
          fullName: userDoc.exists()
            ? userDoc.data().name
            : currentUser.displayName
        });
      } else {
        setUser(null);
      }
    });

    return () => unsubscribe();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
        setMessage("Login successful!");
      } else {
        if (!name.trim()) {
          setMessage("Please enter your full name.");
          setLoading(false);
          return;
        }

        const result = await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );

        await updateProfile(result.user, {
          displayName: name
        });

        await setDoc(doc(db, "users", result.user.uid), {
          name: name,
          email: email,
          createdAt: serverTimestamp()
        });

        setMessage("Registration successful!");
      }

      setEmail("");
      setPassword("");
      setName("");
    } catch (error) {
      const errors = {
        "auth/email-already-in-use": "Email already registered.",
        "auth/invalid-email": "Invalid email address.",
        "auth/weak-password": "Password must contain at least 6 characters.",
        "auth/invalid-credential": "Incorrect email or password.",
        "auth/network-request-failed": "Check your internet connection."
      };

      setMessage(errors[error.code] || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setMessage("");
  };

  if (user) {
    return (
      <div className="page">
        <div className="dashboard">
          <div className="success-icon">✓</div>

          <h1>Welcome!</h1>

          <p>You have successfully logged in.</p>

          <div className="user-info">
            <h3>User Details</h3>
            <p><strong>Name:</strong> {user.fullName || user.displayName || "User"}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>User ID:</strong> {user.uid}</p>
          </div>

          <button className="main-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="login-card">

        <div className="logo">AUTHIFY</div>

        <h1>{isLogin ? "Welcome Back!" : "Create Account"}</h1>

        <p className="subtitle">
          {isLogin
            ? "Login to access your account"
            : "Register to get started"}
        </p>

        <div className="toggle-buttons">
          <button
            className={isLogin ? "active" : ""}
            onClick={() => {
              setIsLogin(true);
              setMessage("");
            }}
          >
            Login
          </button>

          <button
            className={!isLogin ? "active" : ""}
            onClick={() => {
              setIsLogin(false);
              setMessage("");
            }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit}>

          {!isLogin && (
            <div className="input-group">
              <label>Full Name</label>
              <input
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="input-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength="6"
              required
            />
          </div>

          {message && (
            <div className="message">{message}</div>
          )}

          <button
            type="submit"
            className="main-button"
            disabled={loading}
          >
            {loading
              ? "Please wait..."
              : isLogin
                ? "Login"
                : "Create Account"}
          </button>

        </form>

        <p className="footer-text">
          Secure Authentication powered by Firebase
        </p>

      </div>
    </div>
  );
}

export default App;