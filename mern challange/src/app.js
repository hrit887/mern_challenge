import React, { useState } from 'react';
import TransactionsTable from './TransactionsTable';
import Statistics from './Statistics';
import BarChart from './BarChart';
import PieChart from './PieChart';

const App = () => {
  const [month, setMonth] = useState('March');

  return (
    <div>
      <h1>MERN Stack Coding Challenge</h1>
      <select onChange={e => setMonth(e.target.value)} value={month}>
        <option>January</option>
        <option>February</option>
        <option>March</option>
        <option>April</option>
        <option>May</option>
        <option>June</option>
        <option>July</option>
        <option>August</option>
        <option>September</option>
        <option>October</option>
        <option>November</option>
        <option>December</option>
      </select>
      <Statistics month={month} />
      <TransactionsTable month={month} />
      <BarChart month={month} />
      <PieChart month={month} />
    </div>
  );
};

export default App;
