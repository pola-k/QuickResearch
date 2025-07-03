import "./Loader.css";

export default function Loader() {
  return (
    <div className="loader-overlay">
      <div className="loader-box">
        <div className="spinner" />
        <p>Please wait, it may take 4-5 minutes...</p>
      </div>
    </div>
  );
}
