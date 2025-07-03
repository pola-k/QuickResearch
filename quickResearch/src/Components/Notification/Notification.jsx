import './Notification.css';

export default function Notification({ message, type}) {
  return (
    <div className="notification-container">
        <div className={`notification ${type}`}>
            <span className="message">{message}</span>
        </div>
    </div>
  );
}