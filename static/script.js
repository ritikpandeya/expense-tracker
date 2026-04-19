async function fetchTransactions() {
    const res = await fetch('/get');
    let data = await res.json();

    const search = document.getElementById('search').value.toLowerCase();
    const filter = document.getElementById('filter').value;

    if (search)
        data = data.filter(t => t[1].toLowerCase().includes(search));

    if (filter)
        data = data.filter(t => t[3] === filter);

    const list = document.getElementById('list');
    list.innerHTML = '';

    let balance=0, income=0, expense=0;
    let categoryTotals={};

    data.forEach(t=>{
        const amount=Number(t[2]);
        const category=t[3];

        balance+=amount;
        amount>0?income+=amount:expense+=amount;

        categoryTotals[category]=(categoryTotals[category]||0)+Math.abs(amount);

        const li=document.createElement('li');
        li.className=amount>0?'income':'expense';
        li.innerHTML=`${t[1]} <small>${category} | ${t[4]}</small>
        <span>₹${amount}</span>
        <button onclick="deleteTransaction(${t[0]})">x</button>`;
        list.appendChild(li);
    });

    document.getElementById('balance').innerText=`₹${balance}`;
    document.getElementById('income').innerText=`₹${income}`;
    document.getElementById('expense').innerText=`₹${Math.abs(expense)}`;

    drawChart(categoryTotals);
}

async function addTransaction(){
    const text=textValue('text');
    const amount=textValue('amount');
    const category=textValue('category');

    await fetch('/add',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text,amount,category})
    });

    fetchTransactions();
}

function textValue(id){ return document.getElementById(id).value }

async function deleteTransaction(id){
    await fetch(`/delete/${id}`,{method:'DELETE'});
    fetchTransactions();
}

async function clearAll(){
    if(confirm("Delete all transactions?")){
        await fetch('/clear',{method:'DELETE'});
        fetchTransactions();
    }
}

async function exportCSV(){
    await fetch('/export');
    alert("Exported as transactions.csv in project folder");
}

let chart;
function drawChart(data){
    const ctx=document.getElementById('chart');

    if(chart) chart.destroy();

    chart=new Chart(ctx,{
        type:'pie',
        data:{
            labels:Object.keys(data),
            datasets:[{data:Object.values(data)}]
        }
    });
}

function toggleDark(){
    document.body.classList.toggle("dark");
}

fetchTransactions();