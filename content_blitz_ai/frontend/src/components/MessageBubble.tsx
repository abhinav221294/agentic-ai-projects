import ReactMarkdown from "react-markdown";
import TypingIndicator from "./TypingIndicator";

type Props = {

role:string

text:string

}

function MessageBubble({

role,

text

}:Props){

const isUser = role === "User"

return(

<div

style={{

display:"flex",

justifyContent:

isUser

?

"flex-end"

:

"flex-start"

}}

>

<div

style={{

background:

isUser

?

"#2563EB"

:

"#1E293B",

padding:

isUser

?

"16px"

:

"24px",

borderRadius:"16px",

maxWidth:

isUser

?

"60%"

:

"90%",

marginBottom:"20px",

color:"white",

lineHeight:"1.7",

wordBreak:"break-word",

boxShadow:

"0 2px 8px rgba(0,0,0,0.25)"

}}

>

{
    role === "Assistant" && text === "Thinking..."
        ? <TypingIndicator />
        : <ReactMarkdown>{text}</ReactMarkdown>
}
</div>

</div>

)

}

export default MessageBubble