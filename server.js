const {Client}=require("pg")
const express=require("express")

const app=express();
app.use(express.json())

const client=new Client({
	"user":"usermahak",
	"password":"1234",
	"port":5432,
	"database":"mahak"
})

app.get("/",(req,res)=>res.sendFile(`${__dirname}/index.html`))

app.get("/todos",async (req,res)=>{
	const rows=await readTodos();
	res.send(JSON.stringify(rows))
})
app.delete("/todos",async (req,res)=>{
	let result={}
	try{
		
		const reqJson=req.body;
		await deleteTodo(regJson.id);
		result.success=true;
	}
	catch(e)
	{
		result.success=false;
	}
	finally{
		res.setHeader("Content-Type","application/json");
		res.send(JSON.stringify(result));
	}
})

app.listen(8080,()=>console.log("Web server is listening on port 8080"))

start()
async function start()
{
	try{
		await connect();
	/*	const todos=await readTodos();
		console.log(todos)

		const successCreate=await createTodo("Go to trader joes")
		console.log(`Creating was ${successCreate}`)

		const successDelete=await deleteTodo(1)
		console.log(`Deleting was ${successDelete}`)*/
	}
	catch(ex)
	{
		console.log(`Failed to execute ${ex}`)
	}
	/*finally
	{
		await client.end()
		console.log("Cleaned")
	}*/

}

async function connect()
{
	try{
		await client.connect();
	}
	catch(e)
	{
		console.error(`Failed to connect ${e}`)
	}
}

async function readTodos()
{
	try{
		const results=await client.query("select id,text from todos");
		return results.rows;
	}
	catch(e)																														
	{
		return [];
	}
}

async function createTodo(todoText)
{
	try{
		await client.query("insert into todos(text) values ($1,$2)",[11,todoText]);
		return true;
	}
	catch(e)
	{
		return false;
	}
}

async function deleteTodo(id)
{
	try{
		await client.query("delete from todos where id=$1",[id])
		return true
	}
	catch(e)
	{
		return false
	}
}