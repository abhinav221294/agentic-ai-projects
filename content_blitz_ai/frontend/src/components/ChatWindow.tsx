import { useEffect, useRef } from "react"
import MessageBubble from "./MessageBubble"

type Message={

role:string;
text:string;

}

type Props={

messages:Message[]

}

function ChatWindow({

messages

}:Props){
const bottomRef = useRef<HTMLDivElement>(null);

useEffect(() => {

    bottomRef.current?.scrollIntoView({
        behavior: "smooth"
    });

}, [messages]);

return(

<div

style={{

flex:1,

overflowY:"auto",

padding:"20px",

display:"flex",

flexDirection:"column",

gap:"20px"

}}
>

{

messages.map(

(msg,index)=>(

<MessageBubble

key={index}

role={msg.role}

text={msg.text}

/>

)

)
}

<div ref={bottomRef}></div>

</div>

)

}

export default ChatWindow