import React, {useState, useEffect, useRef} from "react";
import axios from 'axios';

// import Button from '@material-ui/core/Button';
// import PhotoCamera from '@material-ui/icons/PhotoCamera';
// import IconButton from '@material-ui/core/IconButton';


// implement useForm later?
const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:5000', // Replace with your Quart server URL
    headers: {
        // 'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'http://localhost:3000', // Allow requests from all origins
        'Access-Control-Allow-Credentials':true
    },
});

function Home() {
    const [embedded, setEmbedded] = useState(false)
    const [answer, setAnswer] = useState(null)
    const [selectedFiles, setSelectedFiles] = useState(null);
    const [question, setQuestion] = useState("");
    const [promptQuestions, setPromptQuestions] = useState([])


    const handleFileChange = (event) => {
        setSelectedFiles([event.target.files[0]]);
      };

    const embedImages = async () => {
        try {
            const formData = new FormData();

            selectedFiles.forEach((file) => {
                formData.append(`files`, file);
            });

            console.log('Triggering embed images endpoint with')
            let result = await axiosInstance.post('/embed_text', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials':true
                },
            });

            if (result === 100) {
                console.log("Error embedding images")
            } else {
                console.log("Embedded images")
                setEmbedded(true)
            }
        } catch (error) {
            console.error('Error triggering Flask endpoint embed images:', error.message);
        }
    }

    const getAnswer = async() => {
        // double check the answer is not empty here
        try {
            // const args = {
            //     "question": question
            // };
            
            console.log('Triggering question with question: ' + question)
            let result = await axios.get('http://127.0.0.1:5000/answer_question', {
                params: {
                    question: question
                }
            }, {
                headers: {
                    'Access-Control-Allow-Origin': 'http://localhost:3000',
                    'Access-Control-Allow-Credentials':true
                },
            });
            setAnswer(result.data["result"])
            console.log(result)

            if (result === 100) {
                console.log("Error in answer question endpoint")
            }
        } catch (error) {
            console.error('Error triggering Flask endpoint get answer:', error.message);
        }
    }

    const promptQuestion = async() => {
        try {
            console.log('Triggering prompt question endpoint')
            let result = await axios.get('http://127.0.0.1:5000/prompt_question', {
                params: {
                    
                }
            }, {
                headers: {
                    'Access-Control-Allow-Origin': 'http://localhost:3000',
                    'Access-Control-Allow-Credentials':true
                },
            });
            console.log(result)

            if (result.status === 100) {
                console.log("Invalid question")
            } else {
                console.log(result)
                setPromptQuestions(result.data["result"])
            }
        } catch (error) {
            console.error('Error triggering Flask endpoint get answer:', error.message);
        }
    }

    return (
        <div>
            Welcome!
            <div>
                <input
                    type="file"
                    accept="image/*, application/pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    id="upload-button"
                />
                <label htmlFor="upload-button" style={{ cursor: 'pointer', padding: '10px 20px', border: '2px solid #ccc', borderRadius: '5px' }}>
                    Select Image
                </label>
                {selectedFiles && <p>Selected file: {selectedFiles[0].name}</p>}
            </div>
            {selectedFiles && <button onClick={embedImages}>Embed image</button>}
            {embedded && 
                <>
                    <div>
                        <input 
                            type="text" 
                            value={question} 
                            onChange={(e) => setQuestion(e.target.value)} // Update the question state
                            placeholder="Ask a question!"
                        />
                        <button onClick={getAnswer}>Get Answer</button>
                        {answer && <p>{answer}</p>}
                    </div>
                    <div>Have the robot ask you a question!</div>
                    <button onClick={promptQuestion}>Get a few questions</button>
                    <p>{promptQuestions}</p>
                </>
            }
        </div>
    );
}

export default Home;