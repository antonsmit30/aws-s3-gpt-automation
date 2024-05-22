import React, { Component } from 'react';
import io from 'socket.io-client';
import AudioRecorder from '../AudioRecorder';
import './Chat.css';
import TypingIndicator from './TypingIndicator';
import eveImage from './eve2.png';
import ReactMarkdown from 'react-markdown';

class ChatComponent extends Component {
    constructor(props) {
        super(props);
        this.state = {
            message: '',
            responses: [],
            isBotTyping: false,
            enableAudio: false,
            // typingMessage: '',
            // nextMessage: ''
        };

        // Creating a reference to the socket
        this.socket = null;
    }

    componentDidMount() {
        // Initialize the socket connection
        this.socket = io(process.env.REACT_APP_BACKEND_URL, { autoConnect: true });

        // Setup event listener for receiving messages
        this.socket.on('server', data => {            

            // Simulate typing delay
            setTimeout(() => {
                this.setState(state => ({
                    responses: [...state.responses, data].slice(-10),
                    isBotTyping: false,
                    // nextMessage: data, 
                    // typingMessage: ''
                }));
                // this.startTypingEffect(data);
            }, 1000); // Adjust the delay as needed
        });
        this.socket.on('user-said', data => {
            console.log("user said", data);
            this.setState(state => {
                // Ensure there are only the last three messages
                const updatedResponses = [...state.responses, data].slice(-10);
                return { responses: updatedResponses };
            });
        });
    }


    componentWillUnmount() {
        // Close the socket connection when the component unmounts
        if (this.socket) {
            this.socket.close();
        }
    }

    // startTypingEffect = (message) => {
    //     let i = 0;
    //     const speed = 50; // Typing speed in milliseconds
    
    //     const type = () => {
    //         if (i < message.length) {
    //             this.setState(prevState => ({ typingMessage: prevState.typingMessage + message.charAt(i) }));
    //             i++;
    //             setTimeout(type, speed);
    //         } else {
    //             // Once the entire message is "typed", add it to the responses and clear typingMessage
    //             this.setState(prevState => ({
    //                 responses: [...prevState.responses, message].slice(-10),
    //                 typingMessage: '',
    //                 nextMessage: ''
    //             }));
    //         }
    //     };
    
    //     type();
    // };

    sendMessage = () => {
        if (this.socket) {
            const userMessage = {
                data: this.state.message, // Display the user's message
                bot_id: 'User', // Distinguish it as a user message
                isUser: true // Flag to identify user messages
            };
            this.socket.emit('client', this.state.message, this.state.enableAudio);
            this.setState({ isBotTyping: true });
            this.setState(state => ({
                responses: [...state.responses, userMessage].slice(-10),
                message: ''
            }));
        }
    };

    sendProceedMessage = () => {
        if (this.socket) {
            const userMessage = {
                data: "Proceed", // Display the user's message
                bot_id: 'User', // Distinguish it as a user message
                isUser: true // Flag to identify user messages
            };
            this.socket.emit('client', "Proceed", this.state.enableAudio);
            this.setState({ isBotTyping: true });
            this.setState(state => ({
                responses: [...state.responses, userMessage].slice(-10),
                message: ''
            }));
        }
    };

    handleMessageChange = (event) => {
        this.setState({ message: event.target.value });
    };

    renderMessageContent = (message, isUser) => {
        // Apply special rendering for bot's message containing code snippet
        if (!isUser) {
            const codeSnippetRegex = /```([^`]+)```/s;
            const match = message.match(codeSnippetRegex);
            if (match) {
                const codeSnippet = match[1];
                const messageParts = message.split(codeSnippetRegex);
                return (
                    <>
                        <ReactMarkdown>{messageParts[0]}</ReactMarkdown>
                        <pre><code>{codeSnippet}</code></pre>
                        <ReactMarkdown>{messageParts[2]}</ReactMarkdown>
                    </>
                );
            }
        }
        return <ReactMarkdown>{message}</ReactMarkdown>;
    };

    myEveImage = (user) => {
        if (user !== "User" && user !== "MaybeUser") {
            return (
                <div className='Eve col-sm img-fluid'>

                    <img className="img-thumbnail" src={eveImage} height="70" width="70" alt="Eve" />

                </div>
            
            )
        } else {
        return null;
        }
    }


    renderMessageCard(response, index) {
        // Different styling for user and bot messages
        const cardClass = response.bot_id === "User" ? "alert alert-primary row": response.bot_id === "MaybeUser" ? "alert alert-info row" : "alert alert-secondary row";
        const sender = response.bot_id === "User" ? "You": response.bot_id === "MaybeUser" ? "Your message transcribed" : "Bot";
        console.log("response before render", response);

        let messageContent;
        // if (response.type === "audio") {
            
        //     const audioSrc = `data:audio/mpeg;base64,${response.data}`;
        //     // messageContent = <audio controls src={audioSrc} />; // disabling this to test playing automatically
        //     const audio = new Audio(audioSrc);
        //     audio.play();
        if (response.type === "audio") {
            const audioSrc = `data:audio/mpeg;base64,${response.data}`;
            // Play audio only if enableAudio is true
            if (this.state.enableAudio) {
                const audio = new Audio(audioSrc);
                audio.play().then(() => {
                    this.removeAudioFromState(index);
                }).catch(e => console.error("Error playing audio:", e));
            } else {
                // If audio is not enabled, immediately remove it from state
                this.removeAudioFromState(index);
            }
            return null;
        } else {
            // messageContent = this.renderMessageContent(response.data, response.isUser);
            messageContent = this.renderMessageContent(response.data, response.bot_id === "User" || response.bot_id === "MaybeUser");
        }

        return (
            <div className='container'>
                {/* {this.myEveImage(response.bot_id)} */}
            
            <div key={index} className={cardClass}>
                
                {/* <strong>{sender}:</strong> {this.renderMessageContent(response.data, response.isUser)} */}
                <div>{this.myEveImage(response.bot_id)}</div><div class="col-sm"><strong>{sender}:</strong> { messageContent }</div>
                {/* <strong>{sender}:</strong> { messageContent } */}
            </div>
            </div>
        );
    }

    removeAudioFromState = (index) => {
        this.setState(state => ({
            responses: state.responses.filter((_, idx) => idx !== index)
        }));
    };    

    sendAudioToServer = (audioBlob) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64String = reader.result.replace(/^data:.+;base64,/, '');
            if (this.socket) {
                this.socket.emit('audio-message', base64String, this.state.enableAudio);
            }
        };
        reader.readAsDataURL(audioBlob);
        this.setState({ isBotTyping: true });
    };

    enableAudio = () => {
        this.setState({ enableAudio: true });
    }

    disableAudio = () => {
        this.setState({ enableAudio: false });
    }

    // render audio button and change color depending on state
    renderAudioButton() {

        return (
            <div>
                {this.state.enableAudio === false
                    ? <button className="btn btn-outline-primary" onClick={this.enableAudio}>Enable Audio</button>
                    : <button className="btn btn-outline-danger" onClick={this.disableAudio}>Disable Audio</button>}
            </div>

        )


    }

    renderClearMemoryButton() {
    
        return (
            <div>
                <button className="btn btn-outline-danger" onClick={this.clearMemory}>Clear Memory</button>
            </div>
        )
    
    }

    render() {
        return (
            <div className="container mt-5">
                <div className="card">
                    <div className="card-header text-center">
                        Automator Bot
                        <div className='container text-center'>
                            <div className='row'>
                            { this.renderAudioButton() }
                            { this.renderClearMemoryButton() }
                            </div>
                        </div>
                        
                    </div>
                    <div className="card-body">
                        <div className="responses">
                            {this.state.responses.map((response, index) => 
                                this.renderMessageCard(response, index)
                            )}
                            {this.state.isBotTyping && <TypingIndicator />}
                        </div>
                        <div className="input-group mt-3">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Type a message..."
                                value={this.state.message}
                                onChange={this.handleMessageChange}
                            />
                            <div className="input-group-append">
                                <button 
                                    className="btn btn-outline-primary"
                                    onClick={this.sendMessage}
                                >Send</button>
                            </div>
                        </div>
                        <div className='container row'>
                        <div className="audio-class">
                        <AudioRecorder onSend={this.sendAudioToServer} />
                        </div>
                        <div className="proceed-class">
                        <button className="btn btn-outline-dark" onClick={this.sendProceedMessage}>Send "Proceed" Message</button>

                        </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default ChatComponent;
