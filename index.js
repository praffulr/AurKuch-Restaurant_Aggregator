const {Client}=require('pg')
const client=new Client({
	user:"usermahak",
	password:"1234",
	port:5432,
	database:"mahak"
})

client.connect()
.then(()=>console.log("Completed successfully"))
.then(()=>client.query("select * from employees where name=$1", ["Mahak"]))
.then(results=>console.table(results.rows))
.catch(e=>console.log(e))
.finally(()=>client.end())