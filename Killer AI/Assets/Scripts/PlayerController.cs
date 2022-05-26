using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController : MonoBehaviour
{

    PlayerMovement playerMove;
    // Start is called before the first frame update
    void Start()
    {
        Screen.lockCursor = true;
        playerMove = GetComponent<PlayerMovement>();
    }

    // Update is called once per frame
    void Update()
    {
        float h = Input.GetAxisRaw("Horizontal");
        float v = Input.GetAxisRaw("Vertical");
        bool isRunning = Input.GetKey(KeyCode.LeftShift);
        bool isJumping = Input.GetKeyDown(KeyCode.Space);
        playerMove.Move(h, v, isRunning, isJumping);


        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");
        playerMove.MoveCamera(mouseX, mouseY);

        if (Input.GetButton("Fire1"))
        {
            playerMove.Shoot();
        }
    }
}
