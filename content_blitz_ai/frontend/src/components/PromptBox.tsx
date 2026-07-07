import { useState } from "react"

type Props = {

  onSend:(query:string)=>void

}

function PromptBox({

  onSend

}:Props){

const [

query,

setQuery

]

=

useState("")

return(

<div

style={{

width:"800px",

margin:"0 auto",

display:"flex",

gap:"12px",

marginTop:"20px"

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

cursor:"pointer",

background:"#2563EB",

border:"none",

color:"white",

fontWeight:"600"

}}

onClick={()=>{

if(!query.trim())

return

onSend(query)

setQuery("")

}}

>

Send

</button>

</div>

)

}

export default PromptBox