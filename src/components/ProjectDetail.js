import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { Paper, Typography, Chip, Box, MenuItem, Select, CircularProgress } from '@mui/material';
import TimeSeriesGraph from './TimeSeriesGraph';
import '../App.css';

const GITHUB_API_URL = "https://api.github.com";
const GITHUB_TOKEN = ""; // add github token here

// Headers for API Authentication
const HEADERS = GITHUB_TOKEN
  ? { Authorization: `token ${GITHUB_TOKEN}` }
  : {};

// Function to fetch issue count based on state, date range, and metric type
async function fetchMetricCount(owner, repo, dateFilter, type) {
  let url = "";
  if (type === "issues") {
    url = `${GITHUB_API_URL}/search/issues?q=repo:${owner}/${repo}+is:issue+${dateFilter}`;
  } else if (type === "prs") {
    url = `${GITHUB_API_URL}/search/issues?q=repo:${owner}/${repo}+is:pr+${dateFilter}`;
  } else if (type === "commits") {
    url = `${GITHUB_API_URL}/repos/${owner}/${repo}/commits?${dateFilter}`;
  }

  try {
    console.log(`Fetching: ${url}`);
    const response = await fetch(url, { headers: HEADERS });
    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

    const data = await response.json();
    return data.total_count || data.length || 0; // GitHub commits return an array
  } catch (error) {
    console.error(`⚠️ Error fetching ${type} for ${dateFilter}: ${error}`);
    return 0;
  }
}

// Function to fetch commits, PRs, and issues (monthly)
async function fetchProjectMetrics(owner, repo) {
  const months = 4;
  let monthlyData = [];

  for (let i = 1; i <= months; i++) {
    const startDate = new Date(new Date().getFullYear(), new Date().getMonth() - i, 1); // First day of month
    const endDate = new Date(new Date().getFullYear(), new Date().getMonth() - i + 1, 0); // Last day of month

    let dateFilter = `since=${startDate.toISOString().split("T")[0]}&until=${endDate.toISOString().split("T")[0]}`;
    const commits = await fetchMetricCount(owner, repo, dateFilter, "commits");

    dateFilter = `created:${startDate.toISOString().split("T")[0]}..${endDate.toISOString().split("T")[0]}`;
    const pullRequests = await fetchMetricCount(owner, repo, dateFilter, "prs");
    const issues = await fetchMetricCount(owner, repo, dateFilter, "issues");

    monthlyData.push({
      time: startDate.toLocaleString("default", { month: "short" }),
      commits,
      pullRequests,
      issues
    });

    // await new Promise(resolve => setTimeout(resolve, 5000)); // Avoid rate limits
  }

  return monthlyData.reverse();
}

const ProjectDetail = () => {
  const { id } = useParams();
  const location = useLocation();
  const project = location.state?.project || {}; // Get project data from state or fallback
  const [selectedMonth, setSelectedMonth] = useState("2024-02"); // Default to the current month
  const [projectMetrics, setProjectMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

   // Sample data for the graphs (Replace with real API data)
  // const projectMetrics = {
  //   weekly: [
  //     { time: "Week 1", commits: 20, pullRequests: 5, issues: 10 },
  //     { time: "Week 2", commits: 30, pullRequests: 8, issues: 7 },
  //     { time: "Week 3", commits: 25, pullRequests: 10, issues: 12 },
  //     { time: "Week 4", commits: 20, pullRequests: 12, issues: 19 },
  //     { time: "Week 4", commits: 30, pullRequests: 16, issues: 2 },
  //     { time: "Week 4", commits: 10, pullRequests: 18, issues: 12 },
  //     { time: "Week 4", commits: 25, pullRequests: 7, issues: 5 }
  //   ],
  //   monthly: [
  //     { time: "Jan", commits: 100, pullRequests: 20, issues: 30 },
  //     { time: "Feb", commits: 120, pullRequests: 25, issues: 35 },
  //     { time: "Mar", commits: 80, pullRequests: 18, issues: 28 },
  //     { time: "Mar", commits: 105, pullRequests: 28, issues: 38 }
  //   ],
  //   yearly: [
  //     { time: "2022", commits: 1200, pullRequests: 300, issues: 500 },
  //     { time: "2023", commits: 1400, pullRequests: 320, issues: 450 },
  //     { time: "2024", commits: 1600, pullRequests: 350, issues: 400 }
  //   ]
  // };

  useEffect(() => {
    if (!project.organization || !project.name) return; // Prevent running if project data is missing

      async function loadProjectMetrics() {
        const REPO_OWNER = project.organization;
        const REPO_NAME = project.name; 
  
        console.log("Fetching project data...");
        const monthlyMetrics = await fetchProjectMetrics(REPO_OWNER, REPO_NAME);
  
        const metrics = {
          weekly: [
            { time: "Week 1", commits: 20, pullRequests: 5, issues: 10 },
            { time: "Week 2", commits: 30, pullRequests: 8, issues: 7 },
            { time: "Week 3", commits: 25, pullRequests: 10, issues: 12 },
            { time: "Week 4", commits: 20, pullRequests: 12, issues: 19 },
            { time: "Week 4", commits: 30, pullRequests: 16, issues: 2 },
            { time: "Week 4", commits: 10, pullRequests: 18, issues: 12 },
            { time: "Week 4", commits: 25, pullRequests: 7, issues: 5 }
          ], // Weekly data will be implemented later
          monthly: monthlyMetrics,
          yearly: [
            { time: "2022", commits: 1200, pullRequests: 300, issues: 500 },
            { time: "2023", commits: 1400, pullRequests: 320, issues: 450 },
            { time: "2024", commits: 1600, pullRequests: 350, issues: 400 }
          ]
        };

        console.log("🔹 Loaded Project Metrics:", metrics);
        setProjectMetrics(metrics);
        setLoading(false);
      }
  
      loadProjectMetrics();
    }, [project.name, project.organization]);

    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
          <CircularProgress color="inherit" />
        </Box>
      );
    }

    // Dummy historical data mapping months to labels
    const historicalLabels = {
      "2024-01": "Crisis",
      "2024-02": "Reviving",
      "2024-03": "Maintaining",
      "2024-04": "Accelerating"
    };
  
    const projectData = {
      name: project.name || `Project ${id}`,
      label: historicalLabels[selectedMonth] || "Unknown",
      activity: 'Medium',
      description: project.description || `Detailed description of Project ${id}.`,
      metrics: 'Commit rate: High, Issue resolution: Medium, PR merge speed: Fast'
    };

  // Define color coding for labels
  const getLabelColor = (label) => {
    switch(label) {
      case 'Accelerating': return '#4CAF50'; // Green
      case 'Consolidating': return '#2196F3'; // Blue
      case 'Maintaining': return '#9E9E9E'; // Grey
      case 'Plateauing': return '#FFEB3B'; // Dark Yellow
      case 'Declining': return '#FF9800'; // Orange
      case 'Crisis': return '#F44336'; // Red
      case 'Reviving': return '#009688'; // Teal
      default: return '#BDBDBD'; // Default fallback color
    }
  };

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
  };


  // Define label insights based on criteria
  const getLabelInsights = (label) => {
    switch(label) {
      case 'Accelerating':
        return {
          description: "Rapid growth in project development.",
          criteria: "Sharp increase in contributors, pull requests, and community engagement.",
          measurement: "More than 30% increase in activity metrics compared to the previous period."
        };
      case 'Consolidating':
        return {
          description: "Steady, moderate growth.",
          criteria: "Moderate increase in contributions, stable community interactions.",
          measurement: "10-20% increase in activity metrics."
        };
      case 'Maintaining':
        return {
          description: "Stable operation without growth or decline.",
          criteria: "Minimal fluctuations in contributions, community activity, and milestones.",
          measurement: "Variations within +/- 5% for all activities."
        };
      case 'Plateauing':
        return {
          description: "Little to no growth, possible onset of stagnation.",
          criteria: "Slow milestone completions, stable but low engagement levels.",
          measurement: "Less than 5% growth and no more than 10% decline in activities."
        };
      case 'Declining':
        return {
          description: "Noticeable decline in project activities.",
          criteria: "Decrease in contributor activity, slower issue resolutions.",
          measurement: "10-20% decrease in key project activities."
        };
      case 'Crisis':
        return {
          description: "Severe decline, project at risk.",
          criteria: "Significant loss of contributors, unresolved issues, unmet milestones.",
          measurement: "More than 30% decrease in key project metrics."
        };
      case 'Reviving':
        return {
          description: "Signs of recovery and improvement.",
          criteria: "Re-engagement of contributors, resolution of issues, increased community activities.",
          measurement: "Improvement from previous decline metrics by 15-30%."
        };
      default:
        return {
          description: "Unknown status",
          criteria: "No data available",
          measurement: "N/A"
        };
    }
  };

  const labelInsights = getLabelInsights(projectData.label);

  return (
    <Paper 
      sx={{ 
        padding: 10, 
        backgroundColor: 'transparent', 
        color: '#fff', 
        borderRadius: '16px', 
        maxWidth: '900px', 
        margin: 'auto', 
        mt: 4
      }}
    >
      <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', marginBottom: 3, textAlign: 'center' }}>
        {projectData.name}
      </Typography>

        {/* Monthly Selector */}
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, marginBottom: 3 }}>
        <Typography variant="h6">Select Month:</Typography>
        <Select value={selectedMonth} onChange={handleMonthChange} sx={{ backgroundColor: '#546E7A', color: '#fff', borderRadius: '8px', padding: '8px' }}>
          {Object.keys(historicalLabels).map((month) => (
            <MenuItem key={month} value={month}>
              {month}
            </MenuItem>
          ))}
        </Select>
      </Box>

      {/* Large Color-Coded Label */}
      <Chip
        label={projectData.label}
        className="big-chip"
        style={{ backgroundColor: getLabelColor(projectData.label), color: '#fff', marginBottom: 16 }}
      />

      {/* Activity Level */}
      <Typography variant="h5" sx={{ fontWeight: 'bold', marginBottom: 2, textAlign: 'center' }}>
        {projectData.activity} Activity
      </Typography>

      {/* Detailed Label Insights */}
      <Typography variant="h6" sx={{ fontWeight: 'bold', marginBottom: 1 }}>
        Label Insights:
      </Typography>
      <Typography variant="body1"><strong>Description:</strong> {labelInsights.description}</Typography>
      <Typography variant="body1"><strong>Criteria:</strong> {labelInsights.criteria}</Typography>
      <Typography variant="body1"><strong>Measurement Method:</strong> {labelInsights.measurement}</Typography>

      {/* Additional Metrics */}
      <Typography paragraph sx={{ mt: 3, fontSize: '1rem' }}>
        <strong>Metrics:</strong> {projectData.metrics}
      </Typography>

      {/* Placeholder for the graph component */}
      <TimeSeriesGraph data={projectMetrics} />
       {/* Time-Series Graph */}
    </Paper>
  );
};

export default ProjectDetail;
