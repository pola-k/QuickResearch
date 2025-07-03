import { useState } from "react";
import "./Chat.css";
import ReactMarkdown from "react-markdown";


export default function Chat(props) 
{
  const [input, setInput] = useState("");

  function handleSubmit() 
  {
    if (!input.trim()) return;

    props.onSendMessage(input);
    setInput("");
  }

  return (
    <div className="chat-container">
      <div className="chat-top-container">
        <h2>Chat</h2>
        <div className="full-width-line"></div>
      </div>

      {props.messages.length === 0 ? (
        <div className="chat-intro">
          <div className="chat-intro-contents">
            <h1>Welcome to Quick Research</h1>
            <p>
              Kickstart your research by uploading your documents and then ask
              anything you need to know. Our AI Chatbot will dive into your
              content and deliver clear, accurate answers instantly!
            </p>
          </div>
        </div>
      ) : (
        <div className="chat-window">
          {props.messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>))}
          
          <div ref={props.last_ref} className="last_child"></div>
        </div>
      )}

      <div className="input-container">
        <div className="input-container-left">
          <textarea name="prompt" id="prompt" className="prompt-textarea" placeholder="Start Typing..." value={input} 
          onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
        </div>
        <div className="input-container-right">
          <h4>Sources {props.sourceCount}</h4>
          <button type="submit" className="submit-btn" onClick={handleSubmit} disabled={props.disabled}>
            <img src="/images/submit-button.svg" alt="Submit" />
          </button>
        </div>
      </div>
    </div>
  );
}
