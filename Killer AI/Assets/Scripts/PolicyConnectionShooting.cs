using System;
using System.Net;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Newtonsoft.Json;
using UnityEngine;

public class PolicyConnectionShooting : MonoBehaviour
{

    // State object for receiving data from remote device.  
    public class StateObject
    {
        // Size of receive buffer.  
        public const int MaxBufferSize = 512;
        // Receive buffer.  
        public byte[] buffer;
    }

    private string unixSocket;
    [HideInInspector]
    public delegate void ResetShouldSendState(Dictionary<string, dynamic> actionDict);
    public delegate void ResetEnvironment();
    
    private ResetShouldSendState resetSendStateCallback;
    private ResetEnvironment resetEnvironmentCallback;


    private Socket client;
    private const int headerLength = 8;
    //private const int ACKLength = 1;
    // private Agent agent;
    // private AgentManager agentManager;
    [HideInInspector]
    public bool isEpisodeOver = false;
    private const int port = 12001;

    void Awake()
    {
        //unixSocket = Application.dataPath + "/Scripts/Agent/python/ai_controller";
        //print(unixSocket);
        // agent = GetComponentInParent<Agent>();
        // agentManager = GetComponentInParent<AgentManager>();
    }


    public void StartConnection(ResetShouldSendState resetSendStateCallback, ResetEnvironment resetEnvironmentCallback)
    {
        this.resetSendStateCallback = resetSendStateCallback;
        this.resetEnvironmentCallback = resetEnvironmentCallback;   
        SetupConnection();
    }

    public void StartConnection(ResetEnvironment resetEnvironmentCallback)
    {
        this.resetEnvironmentCallback = resetEnvironmentCallback;
        SetupConnection();
    }

    private void SetupConnection()
    {
        //client = new Socket(AddressFamily.Unix, SocketType.Stream, ProtocolType.IP);
        //var unixEP = new UnixEndPoint(unixSocket);

        // Establish the remote endpoint for the socket.
        IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());
        IPAddress ipAddress = ipHostInfo.AddressList[0];
        //Debug.Log(ipAddress);
        IPEndPoint remoteEP = new IPEndPoint(ipAddress, port);

        // Create a TCP/IP socket.  
        client = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);
        
        client.BeginConnect(remoteEP,
            new AsyncCallback(ConnectCallback), null);
    }


    private void ConnectCallback(System.IAsyncResult ar)
    {
        try
        {
            client.EndConnect(ar);           
        }
        catch (Exception e)
        {
            Debug.LogError(e.ToString());
        }
    }

    public void SendExplorationSetting(string jsonStr)
    {
        //Debug.Log("SendExplorationSetting");
        byte[] byteData = new byte[headerLength + Encoding.ASCII.GetByteCount(jsonStr)];
        Encoding.ASCII.GetBytes(jsonStr.Length.ToString()).CopyTo(byteData, 0);
        Encoding.ASCII.GetBytes(jsonStr).CopyTo(byteData, headerLength);

        client.BeginSend(byteData, 0, byteData.Length, 0, new AsyncCallback(SendExplorationSettingCallback), null);
    }

    private void SendExplorationSettingCallback(IAsyncResult ar)
    {
        //Debug.Log("SendExplorationSettingCallback");
        client.EndSend(ar);
        //resetSendStateCallback();
    }

    public void SendState(Dictionary<string, dynamic> stateDict)
    {
        // Convert dict to JSON string
        string jsonStr = JsonConvert.SerializeObject(stateDict);

        byte[] byteData = new byte[headerLength + Encoding.ASCII.GetByteCount(jsonStr)];
        Encoding.ASCII.GetBytes(jsonStr.Length.ToString()).CopyTo(byteData, 0);
        Encoding.ASCII.GetBytes(jsonStr).CopyTo(byteData, headerLength);

        client.BeginSend(byteData, 0, byteData.Length, 0, new AsyncCallback(SendStateCallback), null);
    }

    private void SendStateCallback(IAsyncResult ar)
    {
        client.EndSend(ar);
        if(isEpisodeOver)
        {
            ReceiveEnd();
        }
        else
        {
            ReceiveAction();
        }
    }

    private void ReceiveAction()
    {
        // Create the state object.  
        StateObject state = new StateObject();
        state.buffer = new byte[headerLength];
        client.BeginReceive(state.buffer, 0, headerLength, 0,
                            new AsyncCallback(ReceiveActionBody), state);
    }

    private void ReceiveActionBody(IAsyncResult ar)
    {
        StateObject state = (StateObject)ar.AsyncState;
        client.EndReceive(ar);

        int packetLength = int.Parse(Encoding.ASCII.GetString(state.buffer));
        state.buffer = new byte[packetLength];
        client.BeginReceive(state.buffer, 0, packetLength, 0, 
                            new AsyncCallback(ReceiveActionBodyCallback), state);
    }

    private void ReceiveActionBodyCallback(IAsyncResult ar)
    {
        client.EndReceive(ar);

        StateObject state = (StateObject)ar.AsyncState;
        string actionJson = Encoding.ASCII.GetString(state.buffer);
        //Debug.Log(actionJson);
        // agent.SetAction();
        Dictionary<string, dynamic> actionDict = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(actionJson);
        resetSendStateCallback(actionDict);
    }
 
    private void ReceiveEnd()
    {
        //Debug.Log("RECEIVE END");
        // Create the state object.  
        StateObject state = new StateObject();
        state.buffer = new byte[headerLength];
        Debug.Log("ReceiveEnd");
        client.BeginReceive(state.buffer, 0, headerLength, 0,
                            new AsyncCallback(ReceiveEndCallback), state);
    }

    // private void ReceiveEndBody(IAsyncResult ar)
    // {
    //     StateObject state = (StateObject)ar.AsyncState;
    //     client.EndReceive(ar);

    //     int packetLength = int.Parse(Encoding.ASCII.GetString(state.buffer));
    //     state.buffer = new byte[packetLength];
    //     client.BeginReceive(state.buffer, 0, packetLength, 0, 
    //                         new AsyncCallback(ReceiveEndCallback), state);
        
    // }

    private void ReceiveEndCallback(IAsyncResult ar)
    {
        Debug.Log("ReceiveEndCallback");
        StateObject state = (StateObject)ar.AsyncState;
        //Debug.Log("ReceiveEndCallback: " + Encoding.ASCII.GetString(state.buffer));
        client.EndReceive(ar);
        //agentManager.shouldRestart = true;
        resetEnvironmentCallback();
    }
}
