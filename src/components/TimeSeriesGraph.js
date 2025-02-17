import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Box, ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";

const TimeSeriesGraph = ({ data }) => {
  const [timeRange, setTimeRange] = useState("month"); // Default view

  // Function to filter data based on selected time range
  const filterDataByRange = () => {
    if (timeRange === "week") return data.weekly;
    if (timeRange === "year") return data.yearly;
    return data.monthly; // Default to monthly view
  };

  return (
    <Box sx={{ backgroundColor: "#263238", padding: 3, borderRadius: "10px", mt: 4 }}>
      <Typography variant="h5" sx={{ color: "#fff", textAlign: "center", mb: 2 }}>
        Project Activity Over Time
      </Typography>

      {/* Toggle buttons to switch between Week, Month, and Year */}
      <ToggleButtonGroup
        value={timeRange}
        exclusive
        onChange={(event, newRange) => newRange && setTimeRange(newRange)}
        sx={{ display: "flex", justifyContent: "center", mb: 2 }}
      >
        <ToggleButton value="week" sx={{ color: "#fff", borderColor: "#90A4AE" }}>Weekly</ToggleButton>
        <ToggleButton value="month" sx={{ color: "#fff", borderColor: "#90A4AE" }}>Monthly</ToggleButton>
        <ToggleButton value="year" sx={{ color: "#fff", borderColor: "#90A4AE" }}>Yearly</ToggleButton>
      </ToggleButtonGroup>

      {/* Line Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={filterDataByRange()} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" stroke="#fff" />
          <YAxis stroke="#fff" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="commits" stroke="#4CAF50" />
          <Line type="monotone" dataKey="pullRequests" stroke="#FF9800" />
          <Line type="monotone" dataKey="issues" stroke="#F44336" />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default TimeSeriesGraph;
