using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ImitationAgent : MonoBehaviour
{

    private PlayerMovement controller;
    private Health playerHealth;
    private PolicyConnectionShooting policyCon;
    private Environment env;

    private bool shouldReset = false;
    private bool waitingForAction = false, isActionSet = false;
    
    private Action storedAction = new Action();



    
    public float rotSpeed = 1.0f;

    void Start()
    {
        env = GameObject.Find("Environment").GetComponent<Environment>();
        //env.maxEpisodeTime = float.MaxValue;
        controller = GetComponent<PlayerMovement>();
        policyCon = GetComponent<PolicyConnectionShooting>();
        playerHealth = GetComponent<Health>();
        Connect();
        
    }

    // Update is called once per frame
    void Update()
    {
        // print("waitingForAction " + waitingForAction);

        // print("isActionSet " + isActionSet);
        if (env.IsEpisodeTerminated())
        {
            env.Reset();
        }
        else if (!waitingForAction)
        {
            if (isActionSet)
            {
                PerformAction();
            }
            else
            {
                SendState();
            } 
        }
        
    }
    
    private void Connect()
    {    
        policyCon.StartConnection(SetAction, Reset); 
    }

    private void Reset()
    {
        // GameObject[] bullets = GameObject.FindGameObjectsWithTag("Bullet");
        // foreach(GameObject bullet in bullets)
        // {
        //     Destroy(bullet);
        // }

        shouldReset = false; 
    }


    void RecordTransform(float[] pos, float[] rot, Transform objTransform)
    {
        pos[0] = objTransform.position.x;
        pos[1] = objTransform.position.y;
        pos[2] = objTransform.position.z;

        rot[0] = objTransform.rotation.x;
        rot[1] = objTransform.rotation.y;
        rot[2] = objTransform.rotation.z;
        rot[3] = objTransform.rotation.w;
    }
    
    public void SendState()
    {
        State state = new State();
        Dictionary<string, dynamic> stateDict = new Dictionary<string, dynamic>();

        RecordTransform(state.position, state.rotation, transform);  
        foreach(Health enemyHealth in env.enemiesHealth)
        {
            EnemyState enemyState = new EnemyState();
            RecordTransform(enemyState.position, enemyState.rotation, enemyHealth.transform);
            enemyState.health = enemyHealth.health;
            state.enemies.Add(enemyState);
        }
        state.health = playerHealth.health;
        stateDict["state"] = state;

        policyCon.SendState(stateDict);

        waitingForAction = true;
        print("Sending State");
    }
    
    public void SetAction(Dictionary<string, dynamic> actionDict)
    {   

        storedAction.xMouse = float.Parse(actionDict["xMouse"]);

        storedAction.yMouse = float.Parse(actionDict["yMouse"]);
        storedAction.xMove = float.Parse(actionDict["xMove"]);
        storedAction.yMove = float.Parse(actionDict["yMove"]);

        storedAction.isRunning = actionDict["isRunning"] == 0;

        storedAction.isJumping = actionDict["isJumping"] == 0;
        storedAction.isShooting = actionDict["isShooting"] == 0;

        isActionSet = true;
        waitingForAction = false;
        //curStep += 1;
    }


    private void PerformAction()
    {
        storedAction.Print();
        controller.Move(
            storedAction.xMove,
            storedAction.yMove,
            storedAction.isRunning,
            storedAction.isJumping,
            storedAction.isShooting);
        
        controller.MoveCamera(
            storedAction.xMouse,
            storedAction.yMouse);
        isActionSet = false;
    }
}
