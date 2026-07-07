import MessageBubble from "./MessageBubble"

type Message={

role:string

text:string

}

type Props={

messages:Message[]

}

function ChatWindow({

messages

}:Props){

return(

<div

style={{

flex:1,

overflowY:"auto",

width:"800px",

margin:"0 auto",

padding:"20px 0"

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

</div>

)

}

export default ChatWindow