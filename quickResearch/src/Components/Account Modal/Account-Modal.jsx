import "./Account-Modal.css";

export default function AccountModal(props) 
{
  return (
    <div className="account-backdrop" onClick={props.handleClose}>
      <div className="account-container" onClick={(e) => e.stopPropagation()}>
        <h2>Hi {props.name}</h2>
        <div className="logout-container">
          <img src="images/logout-button.svg" alt="Logout" />
          <h2>Logout</h2>
        </div>
      </div>
    </div>
  );
}
