import "./Help-Modal.css";

export default function HelpModal(props) {
  return (
    <>
      {props.show && (
        <div className="modal-backdrop" onClick={() => props.handleHelp(false)}>
          <div className="help-container" onClick={(e) => e.stopPropagation()}>
            <div className="help-top-container">
              <div className="help-top-content">
                <h2>How it Works</h2>
                <img
                  src="images/close-button.svg"
                  alt="Close"
                  className="close-button"
                  onClick={() => props.handleHelp(false)}
                />
              </div>
              <div className="full-width-line"></div>
            </div>
            <div className="help-content">
              <p>
                Welcome to your personal research assistant! Here's how it
                works: First, upload the PDF documents you want to use.
                Once uploaded, simply select the documents you wouldd like the AI to
                use while answering your questions. After that, type in your
                prompt or question, and our smart chatbot will read through your
                selected documents to give you accurate, helpful responses based
                on the content. It is an easy and powerful way to explore your
                information, get insights, and save time!
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
