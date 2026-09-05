import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import { HomePage } from "./pages/HomePage";
import { GamePage } from "./pages/GamePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />

        <Route
          path="/game/:category"
          element={<GamePage />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;