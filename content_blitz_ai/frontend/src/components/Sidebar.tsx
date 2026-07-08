function Sidebar(){

return(

<div

style={{

width:"250px",

background:"#111827",

padding:"20px",

display:"flex",

flexDirection:"column",

gap:"15px",

color:"white",

borderRight:"1px solid #2E3440"

}}

>

<h2

style={{

margin:0

}}

>

Chats

</h2>

<button

style={{

padding:"12px",

borderRadius:"10px",

background:"#2563EB",

color:"white",

border:"none",

cursor:"pointer"

}}

>

+ New Chat

</button>

<div

style={{

padding:"12px",

background:"#1E293B",

borderRadius:"10px",

cursor:"pointer"

}}

>

Blog on AI

</div>

<div

style={{

padding:"12px",

background:"#1E293B",

borderRadius:"10px",

cursor:"pointer"

}}

>

LinkedIn Post

</div>

<div

style={{

padding:"12px",

background:"#1E293B",

borderRadius:"10px",

cursor:"pointer"

}}

>

Research Notes

</div>

</div>

);

}

export default Sidebar;