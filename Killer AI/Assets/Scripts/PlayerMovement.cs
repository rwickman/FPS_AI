using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Action {
        public float xMouse;
        public float yMouse;
        public float xMove;
        public float yMove;
        public bool isRunning;
        public bool isJumping;
        public bool isShooting;

        public void Print()
        {
            string x = "xMouse " + xMouse + "\n";
            x +=  "yMouse " + yMouse + "\n";
            x +=  "xMove " + xMove + "\n";
            x +=  "yMove " + yMove + "\n";
            x +=  "isRunning " + isRunning + "\n";
            x +=  "isJumping " + isJumping + "\n";
            x +=  "isShooting " + isShooting + "\n";
            Debug.Log(x);

        }

        // public Action Clone()
        // {
        //     Action action = new Action();
        // }
}

public class PlayerMovement : MonoBehaviour
{

    [HideInInspector]
    public Action action = new Action();
    public float speed;

    public float yaw = 0.0f, pitch = 0.0f;

    [Range(-60, -15)]
    public int minAngle = -30;
    [Range(30, 80)]
    public int maxAngle = 45;

    public float rotSpeed = 1.0f;
    
    public float[] viewClipValues = {0.25f, 0.5f, 0.75f, 1.0f};

    public GameObject camera;
    public Gun gun;
    public float runFactor = 2.0f;
    public float jumpForce = 5.0f;
    Rigidbody rigidbody;
    int groundLayer = (1<<6);
    CapsuleCollider capCollider;


    // Start is called before the first frame update

    void Start()
    {
        rigidbody = GetComponent<Rigidbody>();
        capCollider = GetComponent<CapsuleCollider>();

    }

    // // Update is called once per frame
    // void Update()
    // {
        
    // }
    public float ClipView(float value)
    {
        if (value == 0.0f)
        {
            return value;
        }

        float absVal = Mathf.Abs(value);
        float clippedVal = viewClipValues[viewClipValues.Length - 1];

        for (int i = 0; i < viewClipValues.Length; i++)
        {
            if(absVal <= viewClipValues[i])
            {
                clippedVal = viewClipValues[i];
                break;
            }
        }

        if(value < 0)
        {
            return -clippedVal;
        }
        else{
            return clippedVal;
        }

    }

    public void MoveCamera(float xMouse, float yMouse)
    {
        xMouse = ClipView(xMouse);
        yMouse = ClipView(yMouse);
        action.xMouse = xMouse;
        action.yMouse = yMouse;

        yaw += rotSpeed * xMouse;
        pitch -= rotSpeed * yMouse;

        
        pitch = Mathf.Clamp(pitch, minAngle, maxAngle);

        Quaternion playerRot = Quaternion.Euler(pitch, yaw, 0.0f);
        transform.rotation = Quaternion.Slerp(transform.rotation, playerRot, 0.75f);
    }

    public void Move(float h, float v, bool isRunning, bool isJumping, bool isShooting)
    {
        action.xMove = h;
        action.yMove = v;
        action.isRunning = isRunning;
        action.isJumping = isJumping;
        action.isShooting = isShooting;
        if (isShooting)
        {
            Shoot();

        }
        
        Vector3 movement = new Vector3(h, 0.0f, v);
        Vector3 forward = transform.forward;
        forward.y = 0.0f;
        float curSpeed;
        if (isRunning)
        {
            curSpeed = speed * runFactor;
        }
        else{
            curSpeed = speed;
        }
        
        transform.position += forward * v  * curSpeed * Time.deltaTime;
        Vector3 right = transform.right;
        right.y = 0.0f;
        transform.position += right * h  * curSpeed * Time.deltaTime;
    
        if (isJumping)
        {
            Jump();
        }
    }

    void Jump()
    {
        if (isGrounded())
        {
            rigidbody.AddForce(new Vector3(0.0f, jumpForce, 0.0f));
        }
        
    }
    // void OnDrawGizmosSelected()
    // {
    //     //get the radius of the players capsule collider, and make it a tiny bit smaller than that
    //     float radius = capCollider.radius * 0.9f;
    //     //get the position (assuming its right at the bottom) and move it up by almost the whole radius
    //     Vector3 pos = transform.position - Vector3.up*radius*1.5f;
    //     // Draw a yellow sphere at the transform's position
    //     Gizmos.color = Color.yellow;
    //     Gizmos.DrawSphere(pos, radius);
    // }
    
    bool isGrounded()
    {
        float radius = capCollider.radius * 0.9f;       
        Vector3 pos = transform.position - Vector3.up*radius*1.5f;
        return Physics.CheckSphere(pos, radius, groundLayer);
    }

    public void Shoot()
    {
        gun.Shoot();
    }
}
