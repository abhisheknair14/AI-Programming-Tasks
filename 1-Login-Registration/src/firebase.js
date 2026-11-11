import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

  const firebaseConfig = {
  apiKey: "AIzaSyCXcklOI2fc3xD8zwFaFa20YjjKO1jc8ow",
  authDomain: "ai-programming-tasks.firebaseapp.com",
  projectId: "ai-programming-tasks",
  storageBucket: "ai-programming-tasks.firebasestorage.app",
  messagingSenderId: "950113266052",
  appId: "1:950113266052:web:8675278ab5ad732fd415d1"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);