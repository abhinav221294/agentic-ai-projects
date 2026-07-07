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

padding:"14px",

borderRadius:"12px",

maxWidth:"70%",

marginBottom:"20px",

color:"white"

}}

>

{text}

</div>

</div>

)

}

export default MessageBubble