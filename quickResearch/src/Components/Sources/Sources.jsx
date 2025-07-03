import { useState, useRef, useEffect } from "react";
import "./Sources.css";

export default function Sources(props) {
  const [selectAll, setSelectAll] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const initialStates = {};
    props.sources.forEach(source => {
      initialStates[source] = false;
    });
    props.setSelectedSources(initialStates);
  }, [props.sources]);


  useEffect(() => {
    const checkedCount = Object.values(props.selectedSources).filter(val => val).length;
    props.onSourceCountChange(checkedCount);
    if (props.sources.length > 0 && checkedCount === props.sources.length) 
    {
      setSelectAll(true);
    } 
    else 
    {
      setSelectAll(false);
    }
    
  }, [props.selectedSources, props.sources.length]);

  function handleCheckboxChange(source) 
  {
    props.setSelectedSources(prev => {
      const updated = {
        ...prev,
        [source]: !prev[source],
      };

      return updated;
    });
  }

  function handleSelectAll(event) 
  {
    const checked = event.target.checked;
    setSelectAll(checked);

    const updatedStates = {};
    props.sources.forEach(source => {
      updatedStates[source] = checked;
    });

    props.setSelectedSources(updatedStates);
  }

  function handleButtonClick() 
  {
    fileInputRef.current.click();
  }
  function handleFileChange(e) 
  {
    const file = e.target.files[0];
    if (file) props.handleSources(e);
  }
  function deleteSource(source)
  {
    props.deleteSource(source)
  }

  return (
    <div className="sources-container">
      <div className="sources-top-container">
        <h2>Sources</h2>
        <div className="full-width-line"></div>
      </div>

      <div className="file-select-input">
        <button className="add-button" onClick={handleButtonClick}>
          <img src="images/add-button.svg" alt="Add" /> Add
        </button>
        <input
          ref={fileInputRef}
          type="file"
          name="new-source"
          id="new-source"
          className="file-input"
          onChange={handleFileChange}
          accept=".pdf"
        />
      </div>

      <div className="select-all-sources-container">
        <h3>Select All Sources</h3>
        <input
          className="select-all-input"
          type="checkbox"
          id="all-sources"
          onChange={handleSelectAll}
          checked={selectAll}
        />
      </div>

      <div className="sources-list">
        {props.sources.map((source, index) => (
          <div className="source" key={index}>
            <h2>{source}</h2>
            <div className="input-buttons-container">
              <img className="delete-btn" src="images/delete-button.svg" alt="Delete Button" onClick={() => deleteSource(source)} />
              <input type="checkbox" className="select-input" checked={props.selectedSources[source] || false} 
              onChange={() => handleCheckboxChange(source)}/>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
