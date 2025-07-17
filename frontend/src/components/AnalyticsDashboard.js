import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  CardBody, 
  CardHeader, 
  CardTitle,
  Row,
  Col,
  Nav,
  NavItem,
  NavLink,
  TabContent,
  TabPane,
  Progress,
  Badge,
  Table,
  Spinner,
  Button
} from 'reactstrap';
import { 
  FaChartLine, 
  FaUsers, 
  FaCalendarAlt, 
  FaEnvelope,
  FaDownload,
  FaTrophy,
  FaExclamationTriangle,
  FaCheckCircle,
  FaHeartbeat
} from 'react-icons/fa';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import Toast from './Toast';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = ({ showToast }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({});
  const [timeRange, setTimeRange] = useState(30);
  const [toast, setToast] = useState(null);

  const fetchAnalyticsData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/analytics/dashboard?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const analyticsData = await response.json();
        setData(analyticsData);
      } else {
        setToast({ type: 'error', message: 'Failed to load analytics data' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading analytics' });
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  const exportData = async (type) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/analytics/export?type=${type}&days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `analytics_${type}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setToast({ type: 'success', message: 'Analytics data exported successfully' });
      } else {
        setToast({ type: 'error', message: 'Failed to export analytics data' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error exporting data' });
    }
  };

  const getHealthBadgeColor = (level) => {
    switch (level) {
      case 'Excellent': return 'success';
      case 'Good': return 'info';
      case 'Fair': return 'warning';
      case 'Needs Attention': return 'danger';
      default: return 'secondary';
    }
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'engagement': return <FaUsers className="text-warning" />;
      case 'retention': return <FaHeartbeat className="text-info" />;
      case 'communication': return <FaEnvelope className="text-primary" />;
      case 'activity': return <FaCalendarAlt className="text-success" />;
      case 'success': return <FaCheckCircle className="text-success" />;
      default: return <FaExclamationTriangle className="text-warning" />;
    }
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner color="primary" />
        <p className="mt-2">Loading analytics...</p>
      </div>
    );
  }

  // Chart configurations
  const engagementChartData = {
    labels: data.event_summary?.monthly_trends?.map(t => t.month) || [],
    datasets: [
      {
        label: 'Events',
        data: data.event_summary?.monthly_trends?.map(t => t.event_count) || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      },
      {
        label: 'Total Attendance',
        data: data.event_summary?.monthly_trends?.map(t => t.total_attendance) || [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1
      }
    ]
  };

  const eventTypeChartData = {
    labels: data.event_summary?.type_stats?.map(t => t.event_type) || [],
    datasets: [
      {
        data: data.event_summary?.type_stats?.map(t => t.event_count) || [],
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40'
        ]
      }
    ]
  };

  const sectionParticipationData = {
    labels: data.member_summary?.section_stats?.map(s => s.section_name) || [],
    datasets: [
      {
        label: 'Average Participation',
        data: data.member_summary?.section_stats?.map(s => s.avg_participation) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };

  return (
    <div className="analytics-dashboard">
      <Card>
        <CardHeader>
          <div className="d-flex justify-content-between align-items-center">
            <CardTitle>
              <FaChartLine className="me-2" />
              Analytics Dashboard
            </CardTitle>
            <div className="d-flex gap-2">
              <select 
                className="form-select form-select-sm"
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                style={{ width: 'auto' }}
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={365}>Last year</option>
              </select>
              <Button
                color="success"
                size="sm"
                onClick={() => exportData('overview')}
              >
                <FaDownload className="me-1" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardBody>
          <Nav tabs>
            <NavItem>
              <NavLink 
                active={activeTab === 'overview'} 
                onClick={() => setActiveTab('overview')}
                style={{ cursor: 'pointer' }}
              >
                <FaChartLine className="me-1" />Overview
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'members'} 
                onClick={() => setActiveTab('members')}
                style={{ cursor: 'pointer' }}
              >
                <FaUsers className="me-1" />Members
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'events'} 
                onClick={() => setActiveTab('events')}
                style={{ cursor: 'pointer' }}
              >
                <FaCalendarAlt className="me-1" />Events
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'health'} 
                onClick={() => setActiveTab('health')}
                style={{ cursor: 'pointer' }}
              >
                <FaHeartbeat className="me-1" />Health
              </NavLink>
            </NavItem>
          </Nav>

          <TabContent activeTab={activeTab}>
            {/* Overview Tab */}
            <TabPane tabId="overview">
              <div className="mt-4">
                <Row>
                  <Col md="3">
                    <Card className="text-white bg-primary mb-3">
                      <CardBody>
                        <div className="d-flex justify-content-between">
                          <div>
                            <h4>{data.overview?.total_members || 0}</h4>
                            <small>Total Members</small>
                          </div>
                          <FaUsers size={30} />
                        </div>
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="3">
                    <Card className="text-white bg-success mb-3">
                      <CardBody>
                        <div className="d-flex justify-content-between">
                          <div>
                            <h4>{data.overview?.recent_events || 0}</h4>
                            <small>Recent Events</small>
                          </div>
                          <FaCalendarAlt size={30} />
                        </div>
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="3">
                    <Card className="text-white bg-info mb-3">
                      <CardBody>
                        <div className="d-flex justify-content-between">
                          <div>
                            <h4>{data.overview?.engagement_rate || 0}%</h4>
                            <small>Engagement Rate</small>
                          </div>
                          <FaChartLine size={30} />
                        </div>
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="3">
                    <Card className="text-white bg-warning mb-3">
                      <CardBody>
                        <div className="d-flex justify-content-between">
                          <div>
                            <h4>{data.communication?.messaging?.total_messages || 0}</h4>
                            <small>Messages Sent</small>
                          </div>
                          <FaEnvelope size={30} />
                        </div>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>

                <Row>
                  <Col md="8">
                    <Card>
                      <CardHeader>
                        <h6>Engagement Trends</h6>
                      </CardHeader>
                      <CardBody>
                        <Line data={engagementChartData} />
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="4">
                    <Card>
                      <CardHeader>
                        <h6>Event Types</h6>
                      </CardHeader>
                      <CardBody>
                        <Doughnut data={eventTypeChartData} />
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>

            {/* Members Tab */}
            <TabPane tabId="members">
              <div className="mt-4">
                <Row>
                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <div className="d-flex justify-content-between">
                          <h6>Top Participants</h6>
                          <Button
                            color="outline-success"
                            size="sm"
                            onClick={() => exportData('members')}
                          >
                            <FaDownload />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardBody>
                        <Table responsive>
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>RSVPs</th>
                              <th>Attendance</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.member_summary?.top_participants?.map((member, index) => (
                              <tr key={index}>
                                <td>
                                  {index === 0 && <FaTrophy className="text-warning me-2" />}
                                  {member.name}
                                </td>
                                <td>{member.total_rsvps}</td>
                                <td>
                                  <Badge color="success">{member.attendance_rate}%</Badge>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <h6>Section Participation</h6>
                      </CardHeader>
                      <CardBody>
                        <Bar data={sectionParticipationData} />
                      </CardBody>
                    </Card>
                  </Col>
                </Row>

                <Row>
                  <Col md="12">
                    <Card>
                      <CardHeader>
                        <h6>Section Statistics</h6>
                      </CardHeader>
                      <CardBody>
                        <Table responsive>
                          <thead>
                            <tr>
                              <th>Section</th>
                              <th>Members</th>
                              <th>Avg Participation</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.member_summary?.section_stats?.map((section, index) => (
                              <tr key={index}>
                                <td>{section.section_name}</td>
                                <td>{section.member_count}</td>
                                <td>
                                  <Progress 
                                    value={section.avg_participation} 
                                    color="info"
                                  >
                                    {section.avg_participation}
                                  </Progress>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>

                {data.member_summary?.inactive_count > 0 && (
                  <Row>
                    <Col md="12">
                      <Card className="border-warning">
                        <CardBody>
                          <div className="d-flex align-items-center">
                            <FaExclamationTriangle className="text-warning me-2" />
                            <strong>{data.member_summary.inactive_count} inactive members</strong>
                            <span className="ms-2 text-muted">
                              (no RSVP activity in the last {timeRange} days)
                            </span>
                          </div>
                        </CardBody>
                      </Card>
                    </Col>
                  </Row>
                )}
              </div>
            </TabPane>

            {/* Events Tab */}
            <TabPane tabId="events">
              <div className="mt-4">
                <Row>
                  <Col md="12">
                    <Card>
                      <CardHeader>
                        <div className="d-flex justify-content-between">
                          <h6>Recent Event Performance</h6>
                          <Button
                            color="outline-success"
                            size="sm"
                            onClick={() => exportData('events')}
                          >
                            <FaDownload />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardBody>
                        <Table responsive>
                          <thead>
                            <tr>
                              <th>Event</th>
                              <th>Date</th>
                              <th>Type</th>
                              <th>Responses</th>
                              <th>Attendance Rate</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.event_summary?.recent_events?.map((event, index) => (
                              <tr key={index}>
                                <td>{event.title}</td>
                                <td>{new Date(event.date).toLocaleDateString()}</td>
                                <td>
                                  <Badge color="secondary">{event.event_type}</Badge>
                                </td>
                                <td>{event.total_responses}</td>
                                <td>
                                  <Progress 
                                    value={event.attendance_rate} 
                                    color={event.attendance_rate > 70 ? 'success' : event.attendance_rate > 50 ? 'warning' : 'danger'}
                                  >
                                    {event.attendance_rate}%
                                  </Progress>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>

            {/* Health Tab */}
            <TabPane tabId="health">
              <div className="mt-4">
                <Row>
                  <Col md="4">
                    <Card>
                      <CardHeader>
                        <h6>Organization Health Score</h6>
                      </CardHeader>
                      <CardBody className="text-center">
                        <div className="display-4 mb-3" style={{ 
                          color: data.health?.health_score >= 80 ? '#28a745' : 
                                 data.health?.health_score >= 60 ? '#17a2b8' :
                                 data.health?.health_score >= 40 ? '#ffc107' : '#dc3545'
                        }}>
                          {data.health?.health_score || 0}
                        </div>
                        <Badge 
                          color={getHealthBadgeColor(data.health?.health_level)}
                          className="mb-3"
                        >
                          {data.health?.health_level}
                        </Badge>
                        <Progress 
                          value={data.health?.health_score || 0} 
                          color={data.health?.health_score >= 80 ? 'success' : 
                                 data.health?.health_score >= 60 ? 'info' :
                                 data.health?.health_score >= 40 ? 'warning' : 'danger'}
                        />
                      </CardBody>
                    </Card>
                  </Col>
                  <Col md="8">
                    <Card>
                      <CardHeader>
                        <h6>Health Components</h6>
                      </CardHeader>
                      <CardBody>
                        {data.health?.component_scores && Object.entries(data.health.component_scores).map(([key, value]) => (
                          <div key={key} className="mb-3">
                            <div className="d-flex justify-content-between mb-1">
                              <span className="text-capitalize">{key}</span>
                              <span>{value}%</span>
                            </div>
                            <Progress 
                              value={value} 
                              color={value >= 80 ? 'success' : value >= 60 ? 'info' : value >= 40 ? 'warning' : 'danger'}
                            />
                          </div>
                        ))}
                      </CardBody>
                    </Card>
                  </Col>
                </Row>

                <Row>
                  <Col md="12">
                    <Card>
                      <CardHeader>
                        <h6>Recommendations</h6>
                      </CardHeader>
                      <CardBody>
                        {data.health?.recommendations?.map((rec, index) => (
                          <div key={index} className={`border-start border-3 border-${rec.priority === 'high' ? 'danger' : rec.priority === 'medium' ? 'warning' : 'success'} ps-3 mb-3`}>
                            <div className="d-flex align-items-start">
                              <div className="me-2 mt-1">
                                {getRecommendationIcon(rec.type)}
                              </div>
                              <div>
                                <h6 className="mb-1">{rec.title}</h6>
                                <p className="mb-0 text-muted">{rec.description}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>
          </TabContent>
        </CardBody>
      </Card>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default AnalyticsDashboard;
