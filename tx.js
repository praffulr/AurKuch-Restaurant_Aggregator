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
		await client.query("BEGIute(N")
		await client.query("insert into employess values($1,$2)",[1008,"Aton"])
		console.log("Inserted a new row")
		await client.query("COMMIT")
	}
	catch(ex)
	{
		console.log('Failed to execute ${ex}')
	}
	finally{
		await client.end()
		console.log("Cleaned")
	}
}