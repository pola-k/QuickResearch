import "./Header.css";

export default function Header(props)
{

    return (
        <>
            <div className="top-container">
                <div className="top-left-container">
                    <img src="images/logo-light.png" alt="Logo" />
                    <input className='title' type="text" value={props.title} onChange={props.changeTitle}/>
                </div>
                <div className="top-right-container">
                    <img src="images/help-button.svg" alt="Help" className="help-button" onClick={()=>props.handleHelp(true)}/>
                    <img src="images/account-button.svg" alt="Profile" className="account-button" onClick={()=>props.handleAccount(!props.showAccount)}/>
                </div>
          </div>
        </>
    )
}