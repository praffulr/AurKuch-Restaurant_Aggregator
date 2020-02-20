const {Client}=require('pg')

const client=new Client({
	user:"usermahak",
	password:"1234",
	port:5432,
	database:"mahak"
})

execute()

async function execute(){
	try{
		await client.connect()  
		console.log("Connected successfully")
		const results=await client.query("select * from employees")
		console.table(results.rows)
	}
	catch(ex)
	{
		console.log("Something wrong happened ${ex}")
	}
	finally
	{
		await client.end()
		console.log("Client disconnected successfully")
	}
}