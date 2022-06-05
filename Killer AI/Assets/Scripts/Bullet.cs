using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Bullet : MonoBehaviour
{
    public float lifeSpanSec = 20f;
    private float startTime;
    public float attackDamage = 2.0f;

    // Start is called before the first frame update
    void Start()
    {
        startTime = Time.time;
    }

    // Update is called once per frame
    void Update()
    {
        if (Time.time - startTime > lifeSpanSec)
        {
            Destroy(gameObject);
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        GameObject hitObj = collision.contacts[0].otherCollider.gameObject;
        if (hitObj.tag == "enemy")
        {
            hitObj.GetComponentInParent<Health>().Damage(attackDamage);
        }
    }
}