using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Enemy : MonoBehaviour
{
    // Stopping distance to player
    
    public float stoppingDist;
    public GameObject player;
    Animator animator;
    bool isAttacking;
    public float attackSpeed;
    public float attackDamage = 1.0f;

    float nextAttackTime = 0.0f;

    
    // Start is called before the first frame update
    void Start()
    {
        //player = GameObject.Find("Player");
        animator = GetComponent<Animator>();
    }

    // Update is called once per frame
    void Update()
    {
        LookTowardsPlayer();
        UpdateAnim();
        if (isAttacking && nextAttackTime <= Time.time)
        {
            Attack();
            nextAttackTime = Time.time + attackSpeed;

        }
    }

    void LookTowardsPlayer()
    {
        Vector3 dir = transform.position - player.transform.position;
        dir.y = 0.0f;
        Quaternion lookRot = Quaternion.LookRotation(dir);
        transform.rotation = lookRot;
    }

    void UpdateAnim()
    {
        float playerDist = Vector3.Distance(transform.position, player.transform.position); 
        if (playerDist <= stoppingDist)
        {
            animator.SetBool("IsAttacking", true);
            if (!isAttacking)
                nextAttackTime = Time.time + attackSpeed / 2;
            isAttacking = true;
            
        }
        else {
            animator.SetBool("IsAttacking", false);
            isAttacking = false;
        }
    }

    void Attack()
    {
        player.GetComponent<Health>().Damage(attackDamage);
    }
}
