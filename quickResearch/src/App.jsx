import './App.css'
import { useState, useEffect, useRef} from 'react';
import Header from './Components/Header/Header.jsx';
import Sources from './Components/Sources/Sources.jsx';
import Chat from './Components/Chat/Chat.jsx';
import HelpModal from './Components/Help Modal/Help-Modal.jsx';
import AccountModal from './Components/Account Modal/Account-Modal.jsx';
import Loader from './Components/Loader/Loader.jsx';
import Notification from './Components/Notification/Notification.jsx';
import axios from "axios"

export default function App() 
{
  const [documentTitle, setDocumentTitle] = useState("My First Research");
  const [sources, setSources] = useState([])
  const [sourceCount, setSourceCount] = useState(0)
  const [showHelp, setShowHelp] = useState(false)
  const [showAccount, setShowAccount] = useState(false)
  const [username, setUsername] = useState("Sameer Khawar")
  const [messages, setMessages] = useState([]);
  const [selectedSources, setSelectedSources] = useState({});
  const [processing, setProcessing] = useState(false);
  const [notification, setNotification] = useState(null);
  const last_ref = useRef(null);
  const [processingQuery, setProcessingQuery] = useState(false);

  useEffect(()=> {
    initialiseMessages();
    initaliseSources();
    const savedTitle = localStorage.getItem("title");
    setDocumentTitle(savedTitle ? JSON.parse(savedTitle) : "My First Research");
  },[])

  useEffect(() => {
    const handleScroll = () => {
      if (last_ref.current) 
      {
        last_ref.current.scrollIntoView({ behavior: "smooth" });
      } 
    };
    handleScroll();
  },[messages])

  useEffect(() =>{
    if(!processingQuery)
    {
      setNotification(null);
    }
  },[processingQuery])

  useEffect(() => {
    if (notification) 
    {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 3000);

      return () => clearTimeout(timer);
    }

    }, [notification]);

  
  async function initialiseMessages()
  {
    try
    {
      const response = await axios.get("http://127.0.0.1:8000/getMessages")
      setMessages(response.data);  
    } 
    catch (error)
    {
      console.error("Error fetching messages:", error);
      setMessages([]);
    } 
  }

  function handleTitleChange(event) 
  {
    setDocumentTitle(event.target.value);
    localStorage.setItem('title', JSON.stringify(event.target.value));
  }

  async function handleSources(e)
  {
    e.preventDefault()
    setProcessing(true);
    const fileName = e.target.files[0].name
    const formData = new FormData();
    formData.append("file", e.target.files[0])
    try 
    {
      await axios.post("http://127.0.0.1:8000/uploadFile", formData, {headers: { "Content-Type": "multipart/form-data" }});
      setSources(prevSources => [...prevSources, fileName]);
      setNotification({message: "File uploaded successfully!", type: "success"});
    } 
    catch (err) 
    {
      setNotification({message: "File upload failed. Please try again.", type: "error"});
      console.error("File upload failed", err);
    } 
    finally 
    {
      setProcessing(false);
    }
  }

  async function initaliseSources()
  {
    try
    {
      const response = await axios.get("http://127.0.0.1:8000/getUploadedFiles")
      setSources(response.data.uploaded_files);
    }
    catch (error)
    {
      console.error("Error fetching sources:", error);
      setSources([]);
    }
  }

  function handleHelp(value)
  {
    setShowHelp(value);
  }

  function handleAccount(value)
  {
    setShowAccount(value);
  }

  async function handleSendMessage(newMessage) 
  {
    if (!newMessage.trim()) return;

    if(processing || processingQuery) return;

    setProcessingQuery(true)
    setNotification({message: "Processing Prompt...", type: "success"})

    setMessages(prev => [...prev, { role: "user", content: newMessage }]);

    const selected = Object.entries(selectedSources).filter(([_, isChecked]) => isChecked).map(([source]) => source);

    try 
    {
      const queryParams = new URLSearchParams();
      queryParams.append("query", newMessage);
      selected.forEach(source => queryParams.append("sources", source));

      const response = await axios.get(`http://127.0.0.1:8000/conversation?${queryParams.toString()}`);
      const reply = response.data.response;
      setMessages(prev => [...prev, { role: "bot", content: reply }]);
      setProcessingQuery(false)
    } 
    catch (error) 
    {
      console.error("Error during conversation:", error);
      setMessages(prev => [...prev, { role: "bot", content: "Sorry, something went wrong." }]);
      setProcessingQuery(false)
    }
  }


  async function deleteSource(fileName)
  {
    try
    {
      await axios.delete("http://127.0.0.1:8000/deleteUploadedFile", {params: { filename: fileName }});
      setSources(prevSources => prevSources.filter(source => source !== fileName));
      setNotification({message: "File deleted successfully!", type: "success"});
    }
    catch (error)
    {
      console.error("Error deleting file:", error);
      setNotification({message: "File deletion failed. Please try again.", type: "error"});
    }
  }

  return (
    <>
        {notification && <Notification message={notification.message} type={notification.type} />}
        {processing && <Loader />}
        <div className="main-container">
          <Header title={documentTitle} changeTitle={handleTitleChange} handleHelp={handleHelp} handleAccount={handleAccount} 
          showAccount={showAccount}/>
          {showHelp && <HelpModal show={showHelp} handleHelp={handleHelp}/>}
          {showAccount && <AccountModal name={username} handleClose={() => setShowAccount(false)} />}
          <div className="cards-layout">
            <Sources sources={sources} handleSources={handleSources} onSourceCountChange={setSourceCount} selectedSources={selectedSources} 
            setSelectedSources={setSelectedSources} deleteSource={deleteSource}/>
            <Chat sourceCount={sourceCount} messages={messages} onSendMessage={handleSendMessage} last_ref={last_ref} disable={processingQuery}/>
          </div>
        </div>
    </>
  )
}