const {Client}=require('pg')
const client=new Client({
	user:"usermahak",
	password:"1234",
	port:5432,
	database:"mahak"
})

client.connect()
.then(()=>console.log("Completed successfully"))
.then(()=>client.query("insert into employees values ($1,$2)",[1001,"John"]))
.then(()=>client.query("select * from employees"))
.then(results=>console.table(results.rows))
.catch(e=>console.log(e))
.finally(()=>client.end())