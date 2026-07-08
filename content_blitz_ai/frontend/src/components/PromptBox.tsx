import { useState } from "react"

type Props = {

  onSend:(query:string)=>void

  loading:boolean

}

function PromptBox({

  onSend,

  loading

}:Props){

const [

query,

setQuery

]

=

useState("")

const handleClick = ()=>{

if(!query.trim())

return

onSend(query)

setQuery("")

}

return(

<div

style={{

display:"flex",

gap:"12px",

paddingBottom:"20px"

}}

>

<input

style={{

flex:1,

padding:"14px",

borderRadius:"10px",

border:"1px solid #333",

background:"#1E293B",

color:"white",

fontSize:"16px"

}}

value={query}

disabled={loading}

onChange={(e)=>

setQuery(

e.target.value

)

}

placeholder="Ask Content Blitz"

/>

<button

style={{

padding:"14px 20px",

borderRadius:"10px",

cursor:"pointer"

}}

disabled={loading}

onClick={handleClick}

>

{

loading

?

"Thinking..."

:

"Send"

}

</button>

</div>

)

}

export default PromptBox